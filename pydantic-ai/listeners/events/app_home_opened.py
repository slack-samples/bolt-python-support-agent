from logging import Logger

from slack_bolt import BoltContext
from slack_sdk import WebClient

from listeners.views.app_home_builder import build_app_home_view
from oauth import authorize_url_generator, installation_store
from oauth.state import generate_state


def handle_app_home_opened(
    client: WebClient, event: dict, context: BoltContext, logger: Logger
):
    """Publish the App Home view when a user opens the app's Home tab."""
    try:
        user_id = event["user"]

        authorize_url = None
        installation = installation_store.find_installation(
            enterprise_id=context.enterprise_id,
            team_id=context.team_id,
            user_id=user_id,
        )
        if not (installation and installation.user_token):
            state = generate_state()
            authorize_url = authorize_url_generator.generate(
                state=state, team=context.team_id
            )

        has_installation = bool(installation and installation.user_token)
        view = build_app_home_view(
            authorize_url=authorize_url, has_installation=has_installation
        )
        client.views_publish(user_id=user_id, view=view)
    except Exception as e:
        logger.exception(f"Failed to publish App Home: {e}")
