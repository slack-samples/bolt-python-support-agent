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
        from oauth import authorize_url_generator, installation_store, state_store

        user_id = context.user_id
        installation_store.delete_installation(
            enterprise_id=context.enterprise_id or "",
            team_id=context.team_id or "",
            user_id=user_id,
        )
        state = state_store.issue()
        authorize_url = authorize_url_generator.generate(state)
        view = build_app_home_view(authorize_url=authorize_url)
        client.views_publish(user_id=user_id, view=view)
    except Exception as e:
        logger.exception(f"Failed to handle disconnect: {e}")
