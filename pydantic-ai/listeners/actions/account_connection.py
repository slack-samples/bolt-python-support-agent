from logging import Logger

from slack_bolt import BoltContext
from slack_sdk import WebClient

from listeners.views.app_home_builder import build_app_home_view


def handle_connect_account(ack, logger: Logger):
    """Handle the Connect button click on App Home.

    The Connect button is a URL button that opens the OAuth page in the
    browser, so we only need to acknowledge the action.
    """
    ack()


def handle_disconnect_account(
    ack, client: WebClient, context: BoltContext, logger: Logger
):
    """Handle the Disconnect button click on App Home."""
    ack()
    try:
        from oauth import install_uri, oauth_settings

        user_id = context.user_id
        oauth_settings.installation_store.delete_installation(
                enterprise_id=context.enterprise_id,
                team_id=context.team_id,
                user_id=user_id,
            )
        oauth_settings.installation_store.delete_bot
        view = build_app_home_view(authorize_url=install_uri)
        client.views_publish(user_id=user_id, view=view)
    except Exception as e:
        logger.exception(f"Failed to handle disconnect: {e}")
