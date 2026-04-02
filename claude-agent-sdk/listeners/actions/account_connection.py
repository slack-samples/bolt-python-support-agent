from logging import Logger

from slack_bolt.context.async_context import AsyncBoltContext
from slack_sdk.web.async_client import AsyncWebClient

from listeners.views.app_home_builder import build_app_home_view


async def handle_connect_account(ack, logger: Logger):
    """Handle the Connect button click on App Home.

    The Connect button is a URL button that opens the OAuth page in the
    browser, so we only need to acknowledge the action.
    """
    await ack()


async def handle_disconnect_account(
    ack, client: AsyncWebClient, context: AsyncBoltContext, logger: Logger
):
    """Handle the Disconnect button click on App Home."""
    await ack()
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
        await client.views_publish(user_id=user_id, view=view)
    except Exception as e:
        logger.exception(f"Failed to handle disconnect: {e}")
