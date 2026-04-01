from logging import Logger

from slack_bolt import BoltContext
from slack_sdk import WebClient

from listeners.views.app_home_builder import build_app_home_view

# In-memory set of connected user IDs (placeholder for a real OAuth token store)
connected_users: set[str] = set()


def handle_connect_account(
    ack, client: WebClient, context: BoltContext, logger: Logger
):
    """Handle the Connect button click on App Home."""
    ack()
    try:
        user_id = context.user_id
        connected_users.add(user_id)
        view = build_app_home_view(is_connected=True)
        client.views_publish(user_id=user_id, view=view)
    except Exception as e:
        logger.exception(f"Failed to handle connect: {e}")


def handle_disconnect_account(
    ack, client: WebClient, context: BoltContext, logger: Logger
):
    """Handle the Disconnect button click on App Home."""
    ack()
    try:
        user_id = context.user_id
        connected_users.discard(user_id)
        view = build_app_home_view(is_connected=False)
        client.views_publish(user_id=user_id, view=view)
    except Exception as e:
        logger.exception(f"Failed to handle disconnect: {e}")
