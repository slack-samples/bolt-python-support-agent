from slack_sdk.oauth import AuthorizeUrlGenerator
from slack_sdk.oauth.installation_store import FileInstallationStore

from constants import BOT_SCOPES, SLACK_APP_CLIENT_ID, SLACK_REDIRECT_URI, USER_SCOPES

installation_store = FileInstallationStore(
    base_dir="./data/installations",
    historical_data_enabled=False,
)

authorize_url_generator = AuthorizeUrlGenerator(
    client_id=SLACK_APP_CLIENT_ID,
    redirect_uri=SLACK_REDIRECT_URI,
    scopes=BOT_SCOPES,
    user_scopes=USER_SCOPES,
)

__all__ = ["authorize_url_generator", "installation_store"]
