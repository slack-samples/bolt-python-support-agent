from claude_agent_sdk import tool
from slack_sdk.errors import SlackApiError

from agent.context import casey_deps_var

EMOJI_DESCRIPTION = """\
Add an emoji reaction to the user's current message to acknowledge their sentiment.

Choose an emoji that matches the tone. Suggested emojis by category:
- Gratitude/praise: pray, bow, blush, sparkles, star-struck, heart
- Frustration/confusion: thinking_face, face_with_monocle, sweat_smile, upside_down_face
- Login/password: key, lock, closed_lock_with_key
- Something broken: wrench, hammer_and_wrench, mag
- Performance/slow: hourglass_flowing_sand, snail
- Urgency: rotating_light, zap, fire
- Success/celebration: tada, raised_hands, partying_face, rocket, muscle
- Setup/config: gear, package
- Network/connectivity: satellite, signal_strength
- Agreement/acknowledgment: thumbsup, ok_hand, saluting_face, +1

Do not use eyes (added automatically) or white_check_mark (reserved for mark_resolved).\
"""


@tool(
    name="add_emoji_reaction",
    description=EMOJI_DESCRIPTION,
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
