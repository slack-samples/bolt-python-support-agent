from logging import Logger

from slack_bolt.context.set_suggested_prompts import SetSuggestedPrompts

SUGGESTED_PROMPTS = [
    {"title": "Reset Password", "message": "I need to reset my password"},
    {"title": "Request Access", "message": "I need access to a system or tool"},
    {"title": "Network Issues", "message": "I'm having network connectivity issues"},
]


def handle_assistant_thread_started(
    set_suggested_prompts: SetSuggestedPrompts, logger: Logger
):
    """Handle assistant thread started events by setting suggested prompts."""
    try:
        set_suggested_prompts(
            prompts=SUGGESTED_PROMPTS,
            title="How can I help you today?",
        )
    except Exception as e:
        logger.exception(f"Failed to handle assistant thread started: {e}")
