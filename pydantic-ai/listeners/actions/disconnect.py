from logging import Logger

from slack_bolt import BoltContext
from slack_sdk import WebClient

from listeners.views.app_home_builder import build_app_home_view
from oauth import authorize_url_generator, installation_store
from oauth.state import generate_state


def handle_disconnect(
    ack, client: WebClient, context: BoltContext, logger: Logger
):
    ack()
    try:
        user_id = context.user_id
        enterprise_id = context.enterprise_id
        team_id = context.team_id

        installation_store.delete_installation(
            enterprise_id=enterprise_id, team_id=team_id, user_id=user_id
        )

        state = generate_state()
        authorize_url = authorize_url_generator.generate(state=state, team=team_id)
        view = build_app_home_view(authorize_url=authorize_url)
        client.views_publish(user_id=user_id, view=view)
    except Exception as e:
        logger.exception(f"Failed to disconnect: {e}")
