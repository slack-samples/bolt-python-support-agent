import os

from dotenv import load_dotenv

load_dotenv(dotenv_path=".env", override=False)

SLACK_APP_CLIENT_ID = os.environ["SLACK_APP_CLIENT_ID"]
SLACK_APP_CLIENT_SECRET = os.environ["SLACK_APP_CLIENT_SECRET"]
SLACK_BOT_TOKEN = os.environ.get("SLACK_BOT_TOKEN")
SLACK_APP_TOKEN = os.environ.get("SLACK_APP_TOKEN")
SLACK_REDIRECT_URI = os.environ.get("SLACK_REDIRECT_URI")
PORT = int(os.environ.get("PORT", 3000))

USER_SCOPES = [
    "search:read",
    "channels:history",
    "groups:history",
    "mpim:history",
    "im:history",
    "channels:read",
    "groups:read",
    "canvases:read",
    "users:read",
    "users:read.email",
]
BOT_SCOPES = [
    "app_mentions:read",
    "im:history",
    "im:read",
    "reactions:read",
    "users:read",
]
