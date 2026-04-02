import json
import os
from pathlib import Path
from urllib.parse import urljoin
from dotenv import load_dotenv


from slack_bolt.oauth.oauth_settings import OAuthSettings
from slack_sdk.oauth.installation_store import FileInstallationStore
from slack_sdk.oauth.state_store import FileOAuthStateStore

load_dotenv(dotenv_path=".env", override=False)

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

oauth_settings = OAuthSettings(
    client_id=os.environ.get("SLACK_CLIENT_ID"),
    client_secret=os.environ.get("SLACK_CLIENT_SECRET"),
    redirect_uri=os.environ.get("SLACK_REDIRECT_URI"),
    scopes=BOT_SCOPES,
    user_scopes=USER_SCOPES,
    installation_store=FileInstallationStore(
        base_dir="./data/installations",
    ),
    state_store=FileOAuthStateStore(
        expiration_seconds=600,
        base_dir="./data/states",
    ),
)
install_uri = urljoin(oauth_settings.redirect_uri, oauth_settings.install_path)
