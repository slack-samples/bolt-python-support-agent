from logging import Logger

from agents import Runner
from slack_bolt import BoltContext, Say, SayStream, SetStatus
from slack_sdk import WebClient

from agent import CaseyDeps, casey_agent
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
    # Skip bot messages and message subtypes (edits, deletes, etc.)
    if event.get("bot_id") or event.get("subtype"):
        logger.debug(f"Skipping message: bot_id={event.get('bot_id')}, subtype={event.get('subtype')}")
        return

    is_dm = event.get("channel_type") == "im"
    is_thread_reply = event.get("thread_ts") is not None
    logger.debug(f"Message received: is_dm={is_dm}, is_thread_reply={is_thread_reply}, channel={context.channel_id}, thread_ts={event.get('thread_ts')}")

    if is_dm:
        logger.debug("Handling as DM")
    elif is_thread_reply:
        # Channel thread replies are handled only if the bot is already engaged
        history = conversation_store.get_history(context.channel_id, event["thread_ts"])
        logger.debug(f"Thread reply: has_history={history is not None}")
        if history is None:
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
            message_ts=event["ts"],
        )
        result = Runner.run_sync(casey_agent, input=input_items, context=deps)

        # Stream response in thread with feedback buttons
        streamer = say_stream()
        streamer.append(markdown_text=result.final_output)
        feedback_blocks = create_feedback_block()
        streamer.stop(blocks=feedback_blocks)

        # Store conversation history
        conversation_store.set_history(channel_id, thread_ts, result.to_input_list())

    except Exception as e:
        logger.exception(f"Failed to handle message: {e}")
        say(
            text=f":warning: Something went wrong! ({e})",
            thread_ts=event.get("thread_ts") or event.get("ts"),
        )
