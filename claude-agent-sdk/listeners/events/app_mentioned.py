import random
import re
from logging import Logger

from slack_bolt.agent.async_agent import AsyncBoltAgent
from slack_bolt.context.say.async_say import AsyncSay
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


async def handle_app_mentioned(
    client: AsyncWebClient,
    event: dict,
    agent: AsyncBoltAgent,
    logger: Logger,
    say: AsyncSay,
):
    """Handle @Casey mentions in channels."""
    try:
        channel_id = event["channel"]
        team_id = event.get("team")
        text = event.get("text", "")
        thread_ts = event.get("thread_ts") or event["ts"]
        user_id = event.get("user")

        # Strip the bot mention from the text
        cleaned_text = re.sub(r"<@[A-Z0-9]+>", "", text).strip()

        if not cleaned_text:
            await say(
                text="Hey there! How can I help you? Describe your IT issue and I'll do my best to assist.",
                thread_ts=thread_ts,
            )
            return

        # Add eyes reaction only to the first message (not threaded replies)
        if not event.get("thread_ts"):
            await client.reactions_add(
                channel=channel_id,
                timestamp=event["ts"],
                name="eyes",
            )

        # Set assistant thread status with loading messages
        await client.assistant_threads_setStatus(
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

        # Get session ID for conversation context
        existing_session_id = session_store.get_session(channel_id, thread_ts)

        # Run the agent
        response_text, new_session_id = await run_casey_agent(
            cleaned_text, session_id=existing_session_id
        )

        # Stream response in thread with feedback buttons
        streamer = await agent.chat_stream(
            channel=channel_id,
            recipient_team_id=team_id,  # chat_stream helper cannot infer event["team"] from client
            recipient_user_id=user_id,
            thread_ts=thread_ts,
        )
        await streamer.append(markdown_text=response_text)
        feedback_blocks = create_feedback_block()
        await streamer.stop(blocks=feedback_blocks)

        # Store session ID for future context
        if new_session_id:
            session_store.set_session(channel_id, thread_ts, new_session_id)

        # ~20% chance contextual emoji (lower than DM to be less noisy)
        if random.random() < 0.2:
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
        logger.exception(f"Failed to handle app mention: {e}")
        await say(
            text=f":warning: Something went wrong! ({e})",
            thread_ts=event.get("thread_ts") or event["ts"],
        )
