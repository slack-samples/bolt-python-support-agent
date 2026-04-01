from logging import Logger

from slack_bolt import Ack, BoltContext
from slack_sdk import WebClient


def handle_issue_submission(
    ack: Ack,
    body: dict,
    client: WebClient,
    context: BoltContext,
    logger: Logger,
):
    """Handle modal submission: open DM and post the issue message.

    The message event handler picks up the posted message (identified by
    its ``issue_submission`` metadata) and runs the agent from there.
    """
    ack()

    try:
        user_id = context.user_id
        values = body["view"]["state"]["values"]
        category = values["category_block"]["category_select"]["selected_option"][
            "value"
        ]
        description = values["description_block"]["description_input"]["value"]

        # Open a DM with the user
        dm = client.conversations_open(users=[user_id])
        channel_id = dm["channel"]["id"]

        # Post the issue message with metadata so the message handler can
        # identify it and run the agent on behalf of the original user
        user_message = f"*Category:* {category}\n*Description:* {description}"
        client.chat_postMessage(
            channel=channel_id,
            text=user_message,
            metadata={
                "event_type": "issue_submission",
                "event_payload": {"user_id": user_id},
            },
        )

    except Exception as e:
        logger.exception(f"Failed to handle issue submission: {e}")
