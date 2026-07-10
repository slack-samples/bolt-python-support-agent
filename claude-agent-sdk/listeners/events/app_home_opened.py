import os
from logging import Logger
from urllib.parse import urljoin

from slack_bolt.async_app import AsyncSetSuggestedPrompts
from slack_bolt.context.async_context import AsyncBoltContext
from slack_sdk.web.async_client import AsyncWebClient

from listeners.views.app_home_builder import build_app_home_view

SUGGESTED_PROMPTS = [
    {"title": "Reset Password", "message": "I need to reset my password"},
    {"title": "Request Access", "message": "I need access to a system or tool"},
    {"title": "Network Issues", "message": "I'm having network connectivity issues"},
]


async def handle_app_home_opened(
    client: AsyncWebClient,
    event: dict,
    context: AsyncBoltContext,
    logger: Logger,
    set_suggested_prompts: AsyncSetSuggestedPrompts,
):
    """Handle app_home_opened events.

    Under agent_view, this event fires for both the Home tab and the Messages
    tab (the agent DM). Branch on ``event["tab"]``:
        * ``"messages"`` -- pin suggested prompts to the top of the DM.
        * ``"home"``     -- publish the App Home Block Kit view.
    """
    try:
        if event.get("tab") == "messages":
            await set_suggested_prompts(
                title="How can I help you today?",
                prompts=SUGGESTED_PROMPTS,
            )
            return

        user_id = context.user_id
        install_url = None
        is_connected = False

        if os.environ.get("SLACK_CLIENT_ID"):
            if context.user_token:
                is_connected = True
            else:
                redirect_uri = os.environ.get("SLACK_REDIRECT_URI", "")
                install_url = urljoin(redirect_uri, "/slack/install")

        view = build_app_home_view(
            install_url=install_url,
            is_connected=is_connected,
            bot_user_id=context.bot_user_id,
        )
        await client.views_publish(user_id=user_id, view=view)
    except Exception as e:
        logger.exception(f"Failed to handle app_home_opened: {e}")
