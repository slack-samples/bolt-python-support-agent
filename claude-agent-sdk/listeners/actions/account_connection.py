from logging import Logger

from slack_bolt.context.async_context import AsyncBoltContext
from slack_sdk.web.async_client import AsyncWebClient

from listeners.views.app_home_builder import build_app_home_view

# In-memory set of connected user IDs (placeholder for a real OAuth token store)
connected_users: set[str] = set()


async def handle_connect_account(
    ack, client: AsyncWebClient, context: AsyncBoltContext, logger: Logger
):
    """Handle the Connect button click on App Home."""
    await ack()
    try:
        user_id = context.user_id
        connected_users.add(user_id)
        view = build_app_home_view(is_connected=True)
        await client.views_publish(user_id=user_id, view=view)
    except Exception as e:
        logger.exception(f"Failed to handle connect: {e}")


async def handle_disconnect_account(
    ack, client: AsyncWebClient, context: AsyncBoltContext, logger: Logger
):
    """Handle the Disconnect button click on App Home."""
    await ack()
    try:
        user_id = context.user_id
        connected_users.discard(user_id)
        view = build_app_home_view(is_connected=False)
        await client.views_publish(user_id=user_id, view=view)
    except Exception as e:
        logger.exception(f"Failed to handle disconnect: {e}")
