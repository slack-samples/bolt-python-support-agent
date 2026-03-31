from agents import function_tool
from agents.run_context import RunContextWrapper
from slack_sdk.errors import SlackApiError

from agent.deps import CaseyDeps


@function_tool
async def add_emoji_reaction(
    wrapper: RunContextWrapper[CaseyDeps],
    emoji_name: str,
    on_parent_message: bool = False,
) -> str:
    """Add an emoji reaction to a Slack message.

    By default, reacts to the current message. Set on_parent_message to true to
    react to the thread's parent message instead (e.g. for marking an issue as
    resolved with white_check_mark). Do not use eyes — it is added automatically.

    Args:
        emoji_name: The Slack emoji name without colons (e.g. 'tada', 'wrench', 'white_check_mark').
        on_parent_message: If true, react to the thread's parent message instead of the current message.
    """
    deps = wrapper.context.deps
    timestamp = deps.thread_ts if on_parent_message else deps.message_ts

    try:
        deps.client.reactions_add(
            channel=deps.channel_id,
            timestamp=timestamp,
            name=emoji_name,
        )
        return f"Reacted with :{emoji_name}:"
    except SlackApiError as e:
        return f"Could not add reaction: {e.response['error']}"
