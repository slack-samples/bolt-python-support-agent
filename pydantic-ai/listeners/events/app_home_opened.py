import os
from logging import Logger

from slack_bolt import BoltContext
from slack_sdk import WebClient

from constants import BOT_SCOPES, USER_SCOPES
from listeners.views.app_home_builder import build_app_home_view
from oauth import installation_store
from oauth.state import generate_state


def handle_app_home_opened(
    client: WebClient, event: dict, context: BoltContext, logger: Logger
):
    """Publish the App Home view when a user opens the app's Home tab."""
    try:
        user_id = event["user"]
        team_id = context.team_id
        enterprise_id = context.enterprise_id

        logger.info(team_id)
        logger.info(enterprise_id)

        authorize_url = None
        installation = installation_store.find_installation(
            enterprise_id=None, team_id=team_id, user_id=user_id
        )
        if not (installation and installation.user_token):
            # AuthorizeUrlGenerator()
            # params = {
            #     "client_id": os.environ["SLACK_APP_CLIENT_ID"],
            #     "user_scopes": ",".join(USER_SCOPES),
            #     "bot_scopes":  ",".join(["users:read"]),
            #     "team": team_id,
            # }
            redirect_uri = os.environ.get("SLACK_REDIRECT_URI")
            scopes = ",".join(BOT_SCOPES) if BOT_SCOPES else ""
            user_scopes = ",".join(USER_SCOPES) if USER_SCOPES else ""
            state = generate_state(team_id, enterprise_id)
            authorize_url = (
                f"https://slack.com/oauth/v2/authorize?"
                f"state={state}&"
                f"client_id={os.environ['SLACK_APP_CLIENT_ID']}&"
                f"scope={scopes}&"
                f"user_scope={user_scopes}"
            )
            if redirect_uri is not None:
                authorize_url += f"&redirect_uri={redirect_uri}"
            if team_id is not None:
                authorize_url += f"&team={team_id}"

        view = build_app_home_view(authorize_url=authorize_url)
        client.views_publish(user_id=user_id, view=view)
    except Exception as e:
        logger.exception(f"Failed to publish App Home: {e}")
