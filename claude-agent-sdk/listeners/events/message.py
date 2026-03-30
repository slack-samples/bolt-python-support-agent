import random
from logging import Logger

from slack_bolt.context.async_context import AsyncBoltContext
from slack_bolt.context.say.async_say import AsyncSay
from slack_bolt.context.say_stream.async_say_stream import AsyncSayStream
from slack_bolt.context.set_status.async_set_status import AsyncSetStatus
from slack_sdk.web.async_client import AsyncWebClient

from agent import run_casey_agent
from conversation import session_store
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


async def handle_message(
    client: AsyncWebClient,
    context: AsyncBoltContext,
    event: dict,
    logger: Logger,
    say: AsyncSay,
    say_stream: AsyncSayStream,
    set_status: AsyncSetStatus,
):
    """Handle direct messages sent to Casey."""
    # Skip bot messages and message subtypes (edits, deletes, etc.)
    if event.get("bot_id") or event.get("subtype"):
        return

    # Only handle IM channel type
    if event.get("channel_type") != "im":
        return

    try:
        channel_id = context.channel_id
        text = event.get("text", "")
        thread_ts = event.get("thread_ts") or event["ts"]

        # Get session ID for conversation context
        existing_session_id = session_store.get_session(channel_id, thread_ts)

        # Add eyes reaction only to the first message in a thread
        if not existing_session_id:
            await client.reactions_add(
                channel=channel_id,
                timestamp=event["ts"],
                name="eyes",
            )

        # Set assistant thread status with loading messages
        await set_status(
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
        response_text, new_session_id = await run_casey_agent(
            text, session_id=existing_session_id
        )

        # Stream response in thread with feedback buttons
        streamer = await say_stream()
        await streamer.append(markdown_text=response_text)
        feedback_blocks = create_feedback_block()
        await streamer.stop(blocks=feedback_blocks)

        # Store session ID for future context
        if new_session_id:
            session_store.set_session(channel_id, thread_ts, new_session_id)

        # ~30% chance contextual emoji
        if random.random() < 0.3:
            emoji = random.choice(CONTEXTUAL_EMOJIS)
            await client.reactions_add(
                channel=channel_id,
                timestamp=event["ts"],
                name=emoji,
            )

        # Check for resolution phrases
        output_lower = response_text.lower()
        if any(phrase in output_lower for phrase in RESOLUTION_PHRASES):
            await client.reactions_add(
                channel=channel_id,
                timestamp=event["ts"],
                name="white_check_mark",
            )

    except Exception as e:
        logger.exception(f"Failed to handle DM: {e}")
        await say(
            text=f":warning: Something went wrong! ({e})",
            thread_ts=event.get("thread_ts") or event.get("ts"),
        )
