from claude_agent_sdk import tool
from slack_sdk.errors import SlackApiError

from agent.context import casey_deps_var


@tool(
    name="add_emoji_reaction",
    description=(
        "Add an emoji reaction to a Slack message. By default, reacts to the "
        "current message. Set on_parent_message to true to react to the thread's "
        "parent message instead (e.g. for marking an issue as resolved with "
        "white_check_mark). Do not use eyes — it is added automatically."
    ),
    input_schema={
        "type": "object",
        "properties": {
            "emoji_name": {
                "type": "string",
                "description": "The Slack emoji name without colons (e.g. 'tada', 'wrench', 'white_check_mark').",
            },
            "on_parent_message": {
                "type": "boolean",
                "description": "If true, react to the thread's parent message instead of the current message.",
                "default": False,
            },
        },
        "required": ["emoji_name"],
    },
)
async def add_emoji_reaction_tool(args):
    """Add an emoji reaction to a Slack message."""
    deps = casey_deps_var.get()
    emoji_name = args["emoji_name"]
    on_parent = args.get("on_parent_message", False)
    timestamp = deps.thread_ts if on_parent else deps.message_ts

    try:
        await deps.client.reactions_add(
            channel=deps.channel_id,
            timestamp=timestamp,
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
