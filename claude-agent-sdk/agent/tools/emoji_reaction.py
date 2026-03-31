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
        "thumbs_up for positive progress, +1 for agreement. Do not use eyes (added automatically) "
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
