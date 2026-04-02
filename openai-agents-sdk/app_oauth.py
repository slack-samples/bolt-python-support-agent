import logging
import os

from dotenv import load_dotenv
from slack_bolt import App
from slack_bolt.oauth.oauth_settings import OAuthSettings
from slack_sdk import WebClient

from listeners import register_listeners
from oauth import BOT_SCOPES, USER_SCOPES, installation_store, state_store

load_dotenv(dotenv_path=".env", override=False)

logging.basicConfig(level=logging.DEBUG)

app = App(
    signing_secret=os.environ.get("SLACK_SIGNING_SECRET"),
    token=os.environ.get("SLACK_BOT_TOKEN"),
    client=WebClient(
        base_url=os.environ.get("SLACK_API_URL", "https://slack.com/api"),
        token=os.environ.get("SLACK_BOT_TOKEN"),
    ),
    # Allow bot-posted messages (e.g. issue modal submissions with metadata)
    # to reach the message handler instead of being silently dropped
    ignoring_self_events_enabled=False,
    oauth_settings=OAuthSettings(
        client_id=os.environ.get("SLACK_CLIENT_ID"),
        client_secret=os.environ.get("SLACK_CLIENT_SECRET"),
        scopes=BOT_SCOPES,
        user_scopes=USER_SCOPES,
        installation_store=installation_store,
        state_store=state_store,
    ),
)

register_listeners(app)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 3000))
    print(f"To install the app, navigate to http://localhost:{port}/slack/install")
    app.start(port=port)
