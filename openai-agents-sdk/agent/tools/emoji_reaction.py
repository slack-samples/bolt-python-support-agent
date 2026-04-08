import random

from agents import function_tool
from agents.run_context import RunContextWrapper
from slack_sdk.errors import SlackApiError

from agent.deps import CaseyDeps


@function_tool
async def add_emoji_reaction(
    wrapper: RunContextWrapper[CaseyDeps],
    emoji_name: str,
) -> str:
    """Add an emoji reaction to the user's current message to acknowledge the topic.

    Use any standard Slack emoji that matches the topic or tone of the message.
    Be creative and specific — if someone mentions a dog, use `dog`; if they sound
    frustrated, use `sweat_smile`. The examples below are common picks, not the full set:
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

    Do not use eyes (added automatically) or white_check_mark (reserved for mark_resolved).

    Args:
        emoji_name: The Slack emoji name without colons (e.g. 'tada', 'wrench', 'pray').
    """
    deps = wrapper.context

    # Skip ~15% of reactions to feel more natural
    if random.random() < 0.15:
        return (
            f"Skipped :{emoji_name}: reaction (randomly omitted to avoid over-reacting)"
        )

    try:
        deps.client.reactions_add(
            channel=deps.channel_id,
            timestamp=deps.message_ts,
            name=emoji_name,
        )
        return f"Reacted with :{emoji_name}:"
    except SlackApiError as e:
        return f"Could not add reaction: {e.response['error']}"
