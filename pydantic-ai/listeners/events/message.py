import random
from logging import Logger

from slack_bolt import BoltAgent, Say
from slack_sdk import WebClient

from agent import DEFAULT_MODEL, CaseyDeps, casey_agent
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


def handle_message(client: WebClient, event: dict, agent: BoltAgent, logger: Logger, say: Say):
    """Handle direct messages sent to Casey."""
    # Skip bot messages and message subtypes (edits, deletes, etc.)
    if event.get("bot_id") or event.get("subtype"):
        return

    # Only handle IM channel type
    if event.get("channel_type") != "im":
        return

    try:
        channel_id = event["channel"]
        text = event.get("text", "")
        thread_ts = event.get("thread_ts") or event["ts"]
        user_id = event["user"]

        # Get conversation history
        history = conversation_store.get_history(channel_id, thread_ts)

        # Add eyes reaction only to the first message in a thread
        if history is None:
            client.reactions_add(
                channel=channel_id,
                timestamp=event["ts"],
                name="eyes",
            )

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

        # Run the agent
        deps = CaseyDeps(
            client=client,
            user_id=user_id,
            channel_id=channel_id,
            thread_ts=thread_ts,
        )
        result = casey_agent.run_sync(
            text,
            model=DEFAULT_MODEL,
            deps=deps,
            message_history=history,
        )

        # Stream response in thread with feedback buttons
        streamer = agent.chat_stream()
        streamer.append(markdown_text=result.output)
        feedback_blocks = create_feedback_block()
        streamer.stop(blocks=feedback_blocks)

        # Store conversation history
        conversation_store.set_history(channel_id, thread_ts, result.all_messages())

        # ~30% chance contextual emoji
        if random.random() < 0.3:
            emoji = random.choice(CONTEXTUAL_EMOJIS)
            client.reactions_add(
                channel=channel_id,
                timestamp=event["ts"],
                name=emoji,
            )

        # Check for resolution phrases
        output_lower = result.output.lower()
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
