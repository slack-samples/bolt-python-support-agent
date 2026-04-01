from logging import Logger

from slack_bolt import Ack
from slack_sdk import WebClient

from listeners.views.issue_modal_builder import build_issue_modal


def handle_issue_button(ack: Ack, body: dict, client: WebClient, logger: Logger):
    """Open the issue submission modal when a category button is clicked."""
    ack()

    try:
        category = body["actions"][0]["value"]
        trigger_id = body["trigger_id"]
        modal = build_issue_modal(category)
        client.views_open(trigger_id=trigger_id, view=modal)
    except Exception as e:
        logger.exception(f"Failed to open issue modal: {e}")
