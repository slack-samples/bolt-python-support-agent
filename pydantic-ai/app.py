from http.server import HTTPServer
import logging
from threading import Thread

from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

from constants import PORT, SLACK_APP_TOKEN, SLACK_BOT_TOKEN
from listeners import register_listeners
from oauth.handler import OAuthCallbackHandler

logging.basicConfig(level=logging.INFO)

app = App(
    token=SLACK_BOT_TOKEN,
)

register_listeners(app)

if __name__ == "__main__":
    server = HTTPServer(("0.0.0.0", PORT), OAuthCallbackHandler)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    app.logger.info(f"OAuth callback server listening on port {PORT}")

    handler = SocketModeHandler(app, SLACK_APP_TOKEN)
    handler.start()
