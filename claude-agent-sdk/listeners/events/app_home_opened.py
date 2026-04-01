from logging import Logger

from slack_bolt.context.async_context import AsyncBoltContext
from slack_sdk.web.async_client import AsyncWebClient

from listeners.actions.account_connection import connected_users
from listeners.views.app_home_builder import build_app_home_view


async def handle_app_home_opened(
    client: AsyncWebClient, context: AsyncBoltContext, logger: Logger
):
    """Publish the App Home view when a user opens the app's Home tab."""
    try:
        user_id = context.user_id
        view = build_app_home_view(is_connected=user_id in connected_users)
        await client.views_publish(user_id=user_id, view=view)
    except Exception as e:
        logger.exception(f"Failed to publish App Home: {e}")
