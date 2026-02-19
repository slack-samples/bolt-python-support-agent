import random
from logging import Logger

from agents import Runner
from slack_bolt import Say
from slack_sdk import WebClient

from agent import CaseyDeps, casey_agent
from conversation import conversation_store
from listeners.views.feedback_block import create_feedback_block

RESOLUTION_PHRASES = [
    "resolved",
    "that should fix",
    "you're all set",
    "should be working now",
    "has been reset",
    "ticket created",
]

CONTEXTUAL_EMOJIS = ["+1", "raised_hands", "rocket", "tada", "bulb", "fire"]


def handle_message_im(client: WebClient, event: dict, logger: Logger, say: Say):
    """Handle direct messages sent to Casey."""
    # Skip bot messages and message subtypes (edits, deletes, etc.)
    if event.get("bot_id") or event.get("subtype"):
        return

    # Only handle IM channel type
    if event.get("channel_type") != "im":
        return

    try:
        channel_id = event["channel"]
        team_id = event.get("team")
        text = event.get("text", "")
        thread_ts = event.get("thread_ts") or event["ts"]
        user_id = event["user"]

        # Set assistant thread status with loading messages
        client.assistant_threads_setStatus(
            channel_id=channel_id,
            thread_ts=thread_ts,
            status="Thinking...",
            loading_messages=[
                "Teaching the hamsters to type faster…",
                "Untangling the internet cables…",
                "Consulting the office goldfish…",
                "Polishing up the response just for you…",
                "Convincing the AI to stop overthinking…",
            ],
        )

        # Get conversation history
        history = conversation_store.get_history(channel_id, thread_ts)

        # Add eyes reaction only to the first message in a thread
        if history is None:
            client.reactions_add(
                channel=channel_id,
                timestamp=event["ts"],
                name="eyes",
            )

        # Build input for the agent
        if history:
            input_items = history + [{"role": "user", "content": text}]
        else:
            input_items = text

        # Run the agent
        deps = CaseyDeps(
            client=client,
            user_id=user_id,
            channel_id=channel_id,
            thread_ts=thread_ts,
        )
        result = Runner.run_sync(casey_agent, input=input_items, context=deps)

        # Stream response in thread with feedback buttons
        streamer = client.chat_stream(
            channel=channel_id,
            recipient_team_id=team_id,
            recipient_user_id=user_id,
            thread_ts=thread_ts,
        )
        streamer.append(markdown_text=result.final_output)
        feedback_blocks = create_feedback_block()
        streamer.stop(blocks=feedback_blocks)

        # Store conversation history
        conversation_store.set_history(channel_id, thread_ts, result.to_input_list())

        # ~30% chance contextual emoji
        if random.random() < 0.3:
            emoji = random.choice(CONTEXTUAL_EMOJIS)
            client.reactions_add(
                channel=channel_id,
                timestamp=event["ts"],
                name=emoji,
            )

        # Check for resolution phrases
        output_lower = result.final_output.lower()
        if any(phrase in output_lower for phrase in RESOLUTION_PHRASES):
            client.reactions_add(
                channel=channel_id,
                timestamp=event["ts"],
                name="white_check_mark",
            )

    except Exception as e:
        logger.exception(f"Failed to handle DM: {e}")
        say(
            text=f":warning: Something went wrong! ({e})",
            thread_ts=event.get("thread_ts") or event.get("ts"),
        )
