"""Custom OAuth callback handler for user-scoped tokens."""

import logging
from http.server import BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse

from slack_sdk import WebClient
from slack_sdk.oauth.installation_store.models.installation import Installation

from constants import SLACK_APP_CLIENT_ID, SLACK_APP_CLIENT_SECRET, SLACK_REDIRECT_URI
from oauth import installation_store
from oauth.state import consume_state

logger = logging.getLogger(__name__)

SUCCESS_HTML = (
    "<html><body>"
    "<h1>Authorization successful!</h1>"
    "<p>You can close this window and return to Slack.</p>"
    "</body></html>"
)

FAILURE_HTML = (
    "<html><body>"
    "<h1>Authorization failed</h1>"
    "<p>Something went wrong — please try again.</p>"
    "</body></html>"
)


class OAuthCallbackHandler(BaseHTTPRequestHandler):
    """Handles the GET /slack/oauth_redirect callback."""

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path != "/slack/oauth_redirect":
            self.send_error(404)
            return

        params = parse_qs(parsed.query)
        code = params.get("code", [None])[0]
        state_raw = params.get("state", [None])[0]
        if not code:
            self._respond(400, "Missing code parameter")
            return

        if not state_raw:
            self._respond(400, "Missing state parameter")
            return

        if not consume_state(state_raw):
            self._respond(400, "Invalid state parameter")
            return

        try:
            temp_client = WebClient()
            oauth_response = temp_client.oauth_v2_access(
                client_id=SLACK_APP_CLIENT_ID,
                client_secret=SLACK_APP_CLIENT_SECRET,
                code=code,
                redirect_uri=SLACK_REDIRECT_URI,
            )

            installed_enterprise: dict = oauth_response.get("enterprise") or {}
            installed_team: dict = oauth_response.get("team") or {}
            installer: dict = oauth_response.get("authed_user") or {}

            enterprise_id = installed_enterprise.get("id")
            team_id = installed_team.get("id")
            user_id = installer.get("id")
            user_token = installer.get("access_token")
            user_scopes = installer.get("scope", "")

            if not (user_token and user_id and (team_id or enterprise_id)):
                logger.error(f"Incomplete OAuth response: {oauth_response.data}")
                self._respond(400, "OAuth response missing required fields")
                return

            installation_store.save(
                Installation(
                    enterprise_id=enterprise_id,
                    team_id=team_id,
                    user_id=user_id,
                    user_token=user_token,
                    user_scopes=user_scopes.split(",") if user_scopes else [],
                )
            )
            logger.info(f"Stored user token for team={team_id} user={user_id}")

            self._respond(200, SUCCESS_HTML, content_type="text/html")

        except Exception:
            logger.exception("OAuth token exchange failed")
            self._respond(500, FAILURE_HTML, content_type="text/html")

    def _respond(self, status: int, body: str, content_type: str = "text/plain"):
        self.send_response(status)
        body_bytes = body.encode("utf-8")
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body_bytes)))
        self.end_headers()
        self.wfile.write(body_bytes)
