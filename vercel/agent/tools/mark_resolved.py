import ai
from slack_sdk.errors import SlackApiError

from agent.context import casey_deps_var


@ai.tool
async def mark_resolved() -> str:
    """Mark the user's issue as resolved by adding a green check mark reaction to the parent thread message.

    Call this once when the issue is fully resolved — e.g. password reset
    complete, ticket created, problem fixed.
    """
    deps = casey_deps_var.get()

    try:
        await deps.client.reactions_add(
            channel=deps.channel_id,
            timestamp=deps.thread_ts,
            name="white_check_mark",
        )
        return "Thread marked as resolved."
    except SlackApiError as e:
        return f"Could not mark resolved: {e.response['error']}"
