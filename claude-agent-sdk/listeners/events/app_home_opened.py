import os
from logging import Logger

from slack_bolt.context.async_context import AsyncBoltContext
from slack_sdk.web.async_client import AsyncWebClient

from listeners.views.app_home_builder import build_app_home_view


async def handle_app_home_opened(
    client: AsyncWebClient, context: AsyncBoltContext, logger: Logger
):
    """Publish the App Home view when a user opens the app's Home tab."""
    try:
        user_id = context.user_id
        authorize_url = None
        is_connected = False

        if os.environ.get("SLACK_CLIENT_ID"):
            from oauth import authorize_url_generator, installation_store, state_store

            installation = installation_store.find_installation(
                enterprise_id=context.enterprise_id or "",
                team_id=context.team_id or "",
                user_id=user_id,
            )
            if installation and installation.user_token:
                is_connected = True
            else:
                state = state_store.issue()
                authorize_url = authorize_url_generator.generate(state)

        view = build_app_home_view(
            authorize_url=authorize_url, is_connected=is_connected
        )
        await client.views_publish(user_id=user_id, view=view)
    except Exception as e:
        logger.exception(f"Failed to publish App Home: {e}")
