import os
from logging import Logger

from slack_bolt import BoltContext
from slack_sdk import WebClient

from listeners.views.app_home_builder import build_app_home_view


def handle_app_home_opened(client: WebClient, context: BoltContext, logger: Logger):
    """Publish the App Home view when a user opens the app's Home tab."""
    try:
        user_id = context.user_id
        authorize_url = None
        is_connected = False

        if os.environ.get("SLACK_CLIENT_ID"):
            from oauth import install_uri

            if context.authorize_result.user_token:
                is_connected = True
            else:
                authorize_url = install_uri

        view = build_app_home_view(
            authorize_url=authorize_url, is_connected=is_connected
        )
        client.views_publish(user_id=user_id, view=view)
    except Exception as e:
        logger.exception(f"Failed to publish App Home: {e}")
