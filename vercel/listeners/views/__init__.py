from slack_bolt.async_app import AsyncApp

from .issue_modal import handle_issue_submission


def register(app: AsyncApp):
    app.view("issue_submission")(handle_issue_submission)
