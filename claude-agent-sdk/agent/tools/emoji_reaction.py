from claude_agent_sdk import tool
from slack_sdk.errors import SlackApiError

from agent.context import casey_deps_var


@tool(
    name="add_emoji_reaction",
    description=(
        "Add an emoji reaction to the user's current message to acknowledge "
        "their sentiment. Choose an emoji that matches the tone: pray for "
        "gratitude, wrench for fixes, key for login issues, rotating_light "
        "for urgency, tada for celebrations, thinking_face for confusion, "
        "+1 for positive progress. Do not use eyes (added automatically) "
        "or white_check_mark (reserved for mark_resolved)."
    ),
    input_schema={
        "type": "object",
        "properties": {
            "emoji_name": {
                "type": "string",
                "description": "The Slack emoji name without colons (e.g. 'tada', 'wrench', 'pray').",
            },
        },
        "required": ["emoji_name"],
    },
)
async def add_emoji_reaction_tool(args):
    """Add an emoji reaction to the user's current message."""
    deps = casey_deps_var.get()
    emoji_name = args["emoji_name"]

    try:
        await deps.client.reactions_add(
            channel=deps.channel_id,
            timestamp=deps.message_ts,
            name=emoji_name,
        )
        return {"content": [{"type": "text", "text": f"Reacted with :{emoji_name}:"}]}
    except SlackApiError as e:
        return {
            "content": [
                {
                    "type": "text",
                    "text": f"Could not add reaction: {e.response['error']}",
                }
            ]
        }


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
