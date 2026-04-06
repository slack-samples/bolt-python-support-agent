import json
import os
from pathlib import Path

from slack_sdk.oauth import AuthorizeUrlGenerator
from slack_sdk.oauth.installation_store import FileInstallationStore
from slack_sdk.oauth.state_store import FileOAuthStateStore

_manifest = json.loads(Path("manifest.json").read_text())
BOT_SCOPES = _manifest["oauth_config"]["scopes"]["bot"]

USER_SCOPES = [
    "search:read",
    "channels:history",
    "channels:read",
    "groups:history",
    "groups:read",
    "im:history",
    "mpim:history",
    "users:read",
]

installation_store = FileInstallationStore(
    base_dir="./data/installations",
    historical_data_enabled=False,
)

state_store = FileOAuthStateStore(
    expiration_seconds=600,
    base_dir="./data/states",
)

authorize_url_generator = AuthorizeUrlGenerator(
    client_id=os.environ.get("SLACK_CLIENT_ID", ""),
    redirect_uri=os.environ.get("SLACK_REDIRECT_URI", ""),
    scopes=BOT_SCOPES,
    user_scopes=USER_SCOPES,
)
