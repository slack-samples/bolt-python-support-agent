import re

from slack_bolt.async_app import AsyncApp

from .category_buttons import handle_category_button
from .feedback import handle_feedback


def register(app: AsyncApp):
    app.action(re.compile(r"^category_"))(handle_category_button)
    app.action("feedback")(handle_feedback)
