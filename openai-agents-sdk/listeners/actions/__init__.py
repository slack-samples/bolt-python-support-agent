import re

from slack_bolt import App

from .account_connection import handle_connect_account, handle_disconnect_account
from .issue_buttons import handle_issue_button
from .feedback_buttons import handle_feedback_button


def register(app: App):
    app.action(re.compile(r"^category_"))(handle_issue_button)
    app.action("feedback")(handle_feedback_button)
    app.action("connect_account")(handle_connect_account)
    app.action("disconnect_account")(handle_disconnect_account)
