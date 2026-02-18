from slack_bolt import App

from .issue_modal import handle_issue_submission


def register(app: App):
    app.view("issue_submission")(handle_issue_submission)
