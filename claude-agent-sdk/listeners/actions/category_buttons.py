from logging import Logger

from slack_bolt import Ack
from slack_sdk.web.async_client import AsyncWebClient

from listeners.views.modal_builder import build_issue_modal


async def handle_category_button(
    ack: Ack, body: dict, client: AsyncWebClient, logger: Logger
):
    """Open the issue submission modal when a category button is clicked."""
    await ack()

    try:
        category = body["actions"][0]["value"]
        trigger_id = body["trigger_id"]
        modal = build_issue_modal(category)
        await client.views_open(trigger_id=trigger_id, view=modal)
    except Exception as e:
        logger.exception(f"Failed to open issue modal: {e}")
