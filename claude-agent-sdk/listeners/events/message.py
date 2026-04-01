from logging import Logger

from slack_bolt.context.async_context import AsyncBoltContext
from slack_bolt.context.say.async_say import AsyncSay
from slack_bolt.context.say_stream.async_say_stream import AsyncSayStream
from slack_bolt.context.set_status.async_set_status import AsyncSetStatus
from slack_sdk.web.async_client import AsyncWebClient

from agent import CaseyDeps, run_casey_agent
from thread_context import session_store
from listeners.views.feedback_block import create_feedback_block


async def handle_message(
    client: AsyncWebClient,
    context: AsyncBoltContext,
    event: dict,
    logger: Logger,
    say: AsyncSay,
    say_stream: AsyncSayStream,
    set_status: AsyncSetStatus,
):
    """Handle messages sent to Casey via DM or in threads the bot is part of."""
    # Issue submissions are posted by the bot with metadata so the message
    # handler can run the agent on behalf of the original user.
    is_issue_submission = (
        event.get("metadata", {}).get("event_type") == "issue_submission"
    )

    # Skip message subtypes (edits, deletes, etc.) and bot messages that
    # are not issue submissions.
    if event.get("subtype"):
        return
    if event.get("bot_id") and not is_issue_submission:
        logger.debug(f"Skipping bot message: bot_id={event.get('bot_id')}")
        return

    is_dm = event.get("channel_type") == "im"
    is_thread_reply = event.get("thread_ts") is not None
    logger.debug(
        f"Message received: is_dm={is_dm}, is_thread_reply={is_thread_reply}, channel={context.channel_id}, thread_ts={event.get('thread_ts')}"
    )

    if is_dm:
        logger.debug("Handling as DM")
    elif is_thread_reply:
        # Channel thread replies are handled only if the bot is already engaged
        session = session_store.get_session(context.channel_id, event["thread_ts"])
        logger.debug(f"Thread reply: has_session={session is not None}")
        if session is None:
            logger.debug("Skipping thread reply — bot not engaged in this thread")
            return
    else:
        # Top-level channel messages are handled by app_mentioned
        logger.debug("Skipping top-level channel message")
        return

    try:
        channel_id = context.channel_id
        text = event.get("text", "")
        thread_ts = event.get("thread_ts") or event["ts"]

        # Get session ID for conversation context
        existing_session_id = session_store.get_session(channel_id, thread_ts)

        # Add eyes reaction only to the first message (DMs only — channel
        # threads already have the reaction from the initial app_mention)
        if is_dm and not existing_session_id:
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

        # For issue submissions the bot posted the message, so the real
        # user_id comes from the metadata rather than the event context.
        if is_issue_submission:
            user_id = event["metadata"]["event_payload"]["user_id"]
        else:
            user_id = context.user_id

        # Run the agent with deps for tool access
        deps = CaseyDeps(
            client=client,
            user_id=user_id,
            channel_id=channel_id,
            thread_ts=thread_ts,
            message_ts=event["ts"],
        )
        response_text, new_session_id = await run_casey_agent(
            text, session_id=existing_session_id, deps=deps
        )

        # Stream response in thread with feedback buttons
        streamer = await say_stream()
        await streamer.append(markdown_text=response_text)
        feedback_blocks = create_feedback_block()
        await streamer.stop(blocks=feedback_blocks)

        # Store session ID for future context
        if new_session_id:
            session_store.set_session(channel_id, thread_ts, new_session_id)

    except Exception as e:
        logger.exception(f"Failed to handle message: {e}")
        await say(
            text=f":warning: Something went wrong! ({e})",
            thread_ts=event.get("thread_ts") or event.get("ts"),
        )
