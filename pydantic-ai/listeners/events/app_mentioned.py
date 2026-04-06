import re
from logging import Logger

from slack_bolt import BoltContext, Say, SayStream, SetStatus
from slack_sdk import WebClient

from agent import CaseyDeps, run_casey
from thread_context import conversation_store
from listeners.views.feedback_builder import build_feedback_blocks
from oauth import installation_store


def handle_app_mentioned(
    client: WebClient,
    context: BoltContext,
    event: dict,
    logger: Logger,
    say: Say,
    say_stream: SayStream,
    set_status: SetStatus,
):
    """Handle @Casey mentions in channels."""
    try:
        channel_id = context.channel_id
        text = event.get("text", "")
        thread_ts = event.get("thread_ts") or event["ts"]
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

        # Get conversation history
        history = conversation_store.get_history(channel_id, thread_ts)

        # Look up the user token directly from the installation store rather
        # than context.user_token. Bolt's InstallationStoreAuthorize may fail
        # to resolve the user token when installer-latest is missing or the
        # requesting user differs from the original installer.
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
            message_ts=event["ts"],
            user_token=user_token,
        )
        result = run_casey(cleaned_text, deps, message_history=history)

        # Stream response in thread with feedback buttons
        streamer = say_stream()
        streamer.append(markdown_text=result.output)
        feedback_blocks = build_feedback_blocks()
        streamer.stop(blocks=feedback_blocks)

        # Store conversation history
        conversation_store.set_history(channel_id, thread_ts, result.all_messages())

    except Exception as e:
        logger.exception(f"Failed to handle app mention: {e}")
        say(
            text=f":warning: Something went wrong! ({e})",
            thread_ts=event.get("thread_ts") or event["ts"],
        )
