import random
import re
from logging import Logger

from slack_bolt import BoltContext, Say
from slack_sdk import WebClient

from agent import CaseyDeps, run_casey
from conversation import conversation_store
from listeners.views.feedback_block import create_feedback_block
from oauth import installation_store

RESOLUTION_PHRASES = [
    "resolved",
    "that should fix",
    "you're all set",
    "should be working now",
    "has been reset",
    "ticket created",
]

CONTEXTUAL_EMOJIS = ["+1", "raised_hands", "rocket", "tada", "bulb", "fire"]


def handle_app_mentioned(
    client: WebClient, event: dict, logger: Logger, say: Say, context: BoltContext
):
    """Handle @Casey mentions in channels."""
    try:
        channel_id = context.channel_id
        team_id = context.team_id
        text = event.get("text", "")
        thread_ts = context.thread_ts or event["ts"]
        user_id = context.user_id

        # Strip the bot mention from the text
        cleaned_text = re.sub(r"<@[A-Z0-9]+>", "", text).strip()

        if not cleaned_text:
            say(
                text="Hey there! How can I help you? Describe your IT issue and I'll do my best to assist.",
                thread_ts=thread_ts,
            )
            return

        # Add eyes reaction only to the first message (not threaded replies)
        if not event.get("thread_ts"):
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

        # Get conversation history
        history = conversation_store.get_history(channel_id, thread_ts)

        # Look up user token from the installation store
        installation = installation_store.find_installation(
            enterprise_id=context.enterprise_id,
            team_id=context.team_id,
            user_id=user_id,
        )
        user_token = installation.user_token if installation else None

        # Run the agent
        deps = CaseyDeps(
            client=client,
            user_id=user_id,
            channel_id=channel_id,
            thread_ts=thread_ts,
            user_token=user_token,
        )
        result = run_casey(cleaned_text, deps, message_history=history)

        # Stream response in thread with feedback buttons
        streamer = client.chat_stream(
            channel=channel_id,
            recipient_team_id=team_id,
            recipient_user_id=user_id,
            thread_ts=thread_ts,
        )
        streamer.append(markdown_text=result.output)
        feedback_blocks = create_feedback_block()
        streamer.stop(blocks=feedback_blocks)

        # Store conversation history
        conversation_store.set_history(channel_id, thread_ts, result.all_messages())

        # ~20% chance contextual emoji (lower than DM to be less noisy)
        if random.random() < 0.2:
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
        logger.exception(f"Failed to handle app mention: {e}")
        say(
            text=f":warning: Something went wrong! ({e})",
            thread_ts=event.get("thread_ts") or event["ts"],
        )
