from slack_sdk.models.blocks import (
    ActionsBlock,
    ButtonElement,
)


def create_feedback_block(message_ts: str = "") -> list[dict]:
    """Create feedback block with thumbs up/down buttons.

    Args:
        message_ts: Optional timestamp to identify which message feedback is for.
    """
    block = ActionsBlock(
        block_id=f"feedback_{message_ts}" if message_ts else "feedback",
        elements=[
            ButtonElement(
                text=":thumbsup:",
                action_id="feedback_good",
                value="good",
            ),
            ButtonElement(
                text=":thumbsdown:",
                action_id="feedback_bad",
                value="bad",
            ),
        ],
    )
    return [block.to_dict()]
