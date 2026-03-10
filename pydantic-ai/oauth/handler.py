"""Custom OAuth callback handler for user-scoped tokens."""

import html
import logging
from http.server import BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse

from slack_sdk import WebClient
from slack_sdk.oauth.installation_store.models.installation import Installation

from constants import SLACK_APP_CLIENT_ID, SLACK_APP_CLIENT_SECRET, SLACK_REDIRECT_URI
from oauth import installation_store
from oauth.state import consume_state

logger = logging.getLogger(__name__)

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

            app_id = oauth_response.get("app_id")
            redirect_team = team_id or enterprise_id
            success_html = self._build_success_html(redirect_team, app_id, team_id)
            self._respond(200, success_html, content_type="text/html")

        except Exception:
            logger.exception("OAuth token exchange failed")
            self._respond(500, FAILURE_HTML, content_type="text/html")

    def _build_success_html(self, redirect_team: str, app_id: str, team_id: str) -> str:
        url = html.escape(f"slack://app?team={redirect_team}&id={app_id}")
        browser_url = html.escape(f"https://app.slack.com/client/{team_id}")
        return (
            "<html>"
            "<head>"
            f'<meta http-equiv="refresh" content="0; URL={url}">'
            "<style>"
            "body { padding: 10px 15px; font-family: verdana; text-align: center; }"
            "</style>"
            "</head>"
            "<body>"
            "<h2>Thank you!</h2>"
            "<p>Redirecting to the Slack App... click "
            f'<a href="{url}">here</a>. '
            "If you use the browser version of Slack, click "
            f'<a href="{browser_url}" target="_blank">this link</a> instead.</p>'
            "</body>"
            "</html>"
        )

    def _respond(self, status: int, body: str, content_type: str = "text/plain"):
        self.send_response(status)
        body_bytes = body.encode("utf-8")
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body_bytes)))
        self.end_headers()
        self.wfile.write(body_bytes)
