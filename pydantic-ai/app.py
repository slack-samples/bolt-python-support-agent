from http.server import HTTPServer
import logging
import os
from threading import Thread

from dotenv import load_dotenv
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

from listeners import register_listeners
from oauth.handler import OAuthCallbackHandler, start_oauth_server

load_dotenv(dotenv_path=".env", override=False)

logging.basicConfig(level=logging.DEBUG)

app = App(
    token=os.environ.get("SLACK_BOT_TOKEN"),
)

register_listeners(app)

if __name__ == "__main__":
    server = HTTPServer(("0.0.0.0", int(os.environ.get("PORT", 3000))), OAuthCallbackHandler)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()

    handler = SocketModeHandler(app, os.environ.get("SLACK_APP_TOKEN"))
    handler.start()
