from logging import Logger

from slack_bolt import BoltContext, Say, SayStream, SetStatus
from slack_sdk import WebClient

from agent import CaseyDeps, casey_agent, get_model
from thread_context import conversation_store
from listeners.views.feedback_block import create_feedback_block


def handle_message(
    client: WebClient,
    context: BoltContext,
    event: dict,
    logger: Logger,
    say: Say,
    say_stream: SayStream,
    set_status: SetStatus,
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
        return

    is_dm = event.get("channel_type") == "im"
    is_thread_reply = event.get("thread_ts") is not None

    if is_dm:
        pass
    elif is_thread_reply:
        # Channel thread replies are handled only if the bot is already engaged
        history = conversation_store.get_history(context.channel_id, event["thread_ts"])
        if history is None:
            return
    else:
        # Top-level channel messages are handled by app_mentioned
        return

    try:
        channel_id = context.channel_id
        text = event.get("text", "")
        thread_ts = event.get("thread_ts") or event["ts"]

        # For issue submissions the bot posted the message, so the real
        # user_id comes from the metadata rather than the event context.
        if is_issue_submission:
            user_id = event["metadata"]["event_payload"]["user_id"]
        else:
            user_id = context.user_id

        # Get conversation history
        history = conversation_store.get_history(channel_id, thread_ts)

        # Add eyes reaction only to the first message (DMs only — channel
        # threads already have the reaction from the initial app_mention)
        if is_dm and history is None:
            client.reactions_add(
                channel=channel_id,
                timestamp=event["ts"],
                name="eyes",
            )

        # Set assistant thread status with loading messages
        set_status(
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
            message_ts=event["ts"],
        )
        result = casey_agent.run_sync(
            text,
            model=get_model(),
            deps=deps,
            message_history=history,
        )

        # Stream response in thread with feedback buttons
        streamer = say_stream()
        streamer.append(markdown_text=result.output)
        feedback_blocks = create_feedback_block()
        streamer.stop(blocks=feedback_blocks)

        # Store conversation history
        conversation_store.set_history(channel_id, thread_ts, result.all_messages())

    except Exception as e:
        logger.exception(f"Failed to handle message: {e}")
        say(
            text=f":warning: Something went wrong! ({e})",
            thread_ts=event.get("thread_ts") or event.get("ts"),
        )
