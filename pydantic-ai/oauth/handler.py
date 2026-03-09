"""Custom OAuth callback handler for user-scoped tokens."""

import logging
import os
from http.server import BaseHTTPRequestHandler, HTTPServer
from threading import Thread
from urllib.parse import parse_qs, urlparse

from slack_sdk import WebClient
from slack_sdk.oauth.installation_store.models.installation import Installation

from oauth import installation_store
from oauth.state import verify_state

logger = logging.getLogger(__name__)


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

        state_payload = verify_state(state_raw)
        if state_payload is None:
            self._respond(400, "Invalid state parameter")
            return

        try:
            temp_client = WebClient()
            oauth_response = temp_client.oauth_v2_access(
                client_id=os.environ["SLACK_APP_CLIENT_ID"],
                client_secret=os.environ["SLACK_APP_CLIENT_SECRET"],
                code=code,
                redirect_uri=os.environ.get("SLACK_REDIRECT_URI"),
            )

            authed_user = oauth_response.get("authed_user", {})
            user_token = authed_user.get("access_token")
            user_id = authed_user.get("id")
            user_scopes = authed_user.get("scope", "")
            # TODO: we dont need to fallback to state.get("team_id") we can simplify the state store
            team_id = oauth_response.get("team_id", {}) or state_payload.get("team_id")
            enterprise_id = oauth_response.get("enterprise_id", {}).get(
                "id"
            ) or state_payload.get("enterprise_id")

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

            self._respond(
                200,
                "<html><body><h1>Authorization successful!</h1>"
                "<p>You can close this window and return to Slack.</p>"
                "</body></html>",
                content_type="text/html",
            )

        except Exception:
            logger.exception("OAuth token exchange failed")
            self._respond(500, "Authorization failed - please try again.")

    def _respond(self, status: int, body: str, content_type: str = "text/plain"):
        self.send_response(status)
        body_bytes = body.encode("utf-8")
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body_bytes)))
        self.end_headers()
        self.wfile.write(body_bytes)


def start_oauth_server(port: int):
    """Start the OAuth callback server in a background thread."""
    server = HTTPServer(("0.0.0.0", port), OAuthCallbackHandler)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    logger.info(f"OAuth callback server listening on port {port}")
