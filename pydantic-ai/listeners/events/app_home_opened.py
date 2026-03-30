from logging import Logger

from slack_bolt import BoltContext
from slack_sdk import WebClient

from listeners.views.app_home_builder import build_app_home_view


def handle_app_home_opened(client: WebClient, context: BoltContext, logger: Logger):
    """Publish the App Home view when a user opens the app's Home tab."""
    try:
        user_id = context.user_id
        view = build_app_home_view()
        client.views_publish(user_id=user_id, view=view)
    except Exception as e:
        logger.exception(f"Failed to publish App Home: {e}")
