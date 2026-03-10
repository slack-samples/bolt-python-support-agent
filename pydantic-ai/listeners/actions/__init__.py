import re

from slack_bolt import App

from .category_buttons import handle_category_button
from .disconnect import handle_disconnect
from .feedback import handle_feedback


def register(app: App):
    app.action(re.compile(r"^category_"))(handle_category_button)
    app.action("feedback")(handle_feedback)
    app.action("disconnect_casey")(handle_disconnect)

    @app.action("authorize_casey")
    def authorize_casey(ack):
        ack()
