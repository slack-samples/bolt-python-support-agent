import logging
import os

from dotenv import load_dotenv
from slack_bolt import App
from slack_sdk import WebClient

from agent import get_model
from listeners import register_listeners

load_dotenv(dotenv_path=".env", override=False)
get_model()  # Fail fast if no AI provider key is configured

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
)

register_listeners(app)

if __name__ == "__main__":
    app.start(port=int(os.environ.get("PORT", 3000)))
