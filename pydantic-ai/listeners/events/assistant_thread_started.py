from logging import Logger

from slack_sdk import WebClient

SUGGESTED_PROMPTS = [
    {"title": "Reset Password", "message": "I need to reset my password"},
    {"title": "Request Access", "message": "I need access to a system or tool"},
    {"title": "Network Issues", "message": "I'm having network connectivity issues"},
]


def handle_assistant_thread_started(client: WebClient, event: dict, logger: Logger):
    """Handle assistant thread started events by setting suggested prompts."""
    assistant_thread = event.get("assistant_thread", {})
    channel_id = assistant_thread.get("channel_id")
    thread_ts = assistant_thread.get("thread_ts")

    try:
        client.assistant_threads_setSuggestedPrompts(
            channel_id=channel_id,
            thread_ts=thread_ts,
            title="How can I help you today?",
            prompts=SUGGESTED_PROMPTS,
        )
    except Exception as e:
        logger.exception(f"Failed to handle assistant thread started: {e}")
