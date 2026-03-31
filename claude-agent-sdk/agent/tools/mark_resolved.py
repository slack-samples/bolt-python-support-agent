from claude_agent_sdk import tool
from slack_sdk.errors import SlackApiError

from agent.context import casey_deps_var


@tool(
    name="mark_resolved",
    description=(
        "Mark the user's issue as resolved by adding a green check mark "
        "reaction to the parent thread message. Call this once when the issue "
        "is fully resolved — e.g. password reset complete, ticket created, "
        "problem fixed."
    ),
    input_schema={
        "type": "object",
        "properties": {},
    },
)
async def mark_resolved_tool(args):
    """Mark the thread as resolved with a green check mark on the parent message."""
    deps = casey_deps_var.get()

    try:
        await deps.client.reactions_add(
            channel=deps.channel_id,
            timestamp=deps.thread_ts,
            name="white_check_mark",
        )
        return {"content": [{"type": "text", "text": "Thread marked as resolved."}]}
    except SlackApiError as e:
        return {
            "content": [
                {
                    "type": "text",
                    "text": f"Could not mark resolved: {e.response['error']}",
                }
            ]
        }
