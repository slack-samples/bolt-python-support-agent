import re

from slack_bolt import App

from .feedback_buttons import handle_feedback_button
from .issue_buttons import handle_issue_button


def register(app: App):
    app.action(re.compile(r"^category_"))(handle_issue_button)
    app.action("feedback")(handle_feedback_button)
