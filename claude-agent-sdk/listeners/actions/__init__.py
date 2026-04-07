import re

from slack_bolt.async_app import AsyncApp

from .issue_buttons import handle_issue_button
from .feedback_buttons import handle_feedback_button


def register(app: AsyncApp):
    app.action(re.compile(r"^category_"))(handle_issue_button)
    app.action("feedback")(handle_feedback_button)
