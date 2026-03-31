from pydantic_ai import RunContext
from slack_sdk.errors import SlackApiError

from agent.deps import CaseyDeps


async def add_emoji_reaction(
    ctx: RunContext[CaseyDeps],
    emoji_name: str,
) -> str:
    """Add an emoji reaction to the user's current message to acknowledge their sentiment.

    Choose an emoji that matches the tone: pray for gratitude, wrench for fixes,
    key for login issues, rotating_light for urgency, tada for celebrations,
    thinking_face for confusion, +1 for positive progress. Do not use eyes
    (added automatically) or white_check_mark (reserved for mark_resolved).

    Args:
        ctx: The run context with dependencies.
        emoji_name: The Slack emoji name without colons (e.g. 'tada', 'wrench', 'pray').
    """
    deps = ctx.deps

    try:
        deps.client.reactions_add(
            channel=deps.channel_id,
            timestamp=deps.message_ts,
            name=emoji_name,
        )
        return f"Reacted with :{emoji_name}:"
    except SlackApiError as e:
        return f"Could not add reaction: {e.response['error']}"


async def mark_resolved(
    ctx: RunContext[CaseyDeps],
) -> str:
    """Mark the user's issue as resolved by adding a green check mark reaction to the parent thread message.

    Call this once when the issue is fully resolved — e.g. password reset
    complete, ticket created, problem fixed.

    Args:
        ctx: The run context with dependencies.
    """
    deps = ctx.deps

    try:
        deps.client.reactions_add(
            channel=deps.channel_id,
            timestamp=deps.thread_ts,
            name="white_check_mark",
        )
        return "Thread marked as resolved."
    except SlackApiError as e:
        return f"Could not mark resolved: {e.response['error']}"
