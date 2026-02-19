from logging import Logger

from slack_bolt import Ack
from slack_sdk.web.async_client import AsyncWebClient


async def handle_feedback(ack: Ack, body: dict, client: AsyncWebClient, logger: Logger):
    """Handle thumbs up/down feedback on Casey's responses."""
    await ack()

    try:
        channel_id = body["channel"]["id"]
        user_id = body["user"]["id"]
        message_ts = body["message"]["ts"]
        feedback_value = body["actions"][0]["value"]

        if feedback_value == "good-feedback":
            await client.chat_postEphemeral(
                channel=channel_id,
                user=user_id,
                thread_ts=message_ts,
                text="Glad that was helpful! :tada:",
            )
        else:
            await client.chat_postEphemeral(
                channel=channel_id,
                user=user_id,
                thread_ts=message_ts,
                text="Sorry that wasn't helpful. :slightly_frowning_face: Try rephrasing your question or I can create a support ticket for you.",
            )

        logger.debug(
            f"Feedback received: value={feedback_value}, message_ts={message_ts}"
        )
    except Exception as e:
        logger.exception(f"Failed to handle feedback: {e}")
