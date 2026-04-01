from collections.abc import AsyncIterable

from pydantic_ai import RunContext
from pydantic_ai.messages import (
    AgentStreamEvent,
    FunctionToolCallEvent,
    FunctionToolResultEvent,
)
from slack_sdk.models.messages.chunk import TaskUpdateChunk
from slack_sdk.web.chat_stream import ChatStream

from agent.deps import CaseyDeps

# Human-readable names for Casey's tools
TOOL_DISPLAY_NAMES = {
    "add_emoji_reaction": "Adding reaction",
    "search_knowledge_base": "Searching knowledge base",
    "check_system_status": "Checking system status",
    "create_support_ticket": "Creating support ticket",
    "trigger_password_reset": "Resetting password",
    "lookup_user_permissions": "Looking up permissions",
    "mark_resolved": "Marking resolved",
}


class PlanStreamer:
    """Manages plan display mode task updates for tool calls.

    Wraps a ChatStream and emits TaskUpdateChunk events as tools
    start and complete, giving users real-time visibility into
    the agent's workflow.
    """

    def __init__(self, stream: ChatStream):
        self._stream = stream
        self._task_counter = 0
        self._task_ids: dict[str, str] = {}
        self._tool_names: dict[str, str] = {}

    def tool_started(self, tool_name: str, tool_call_id: str | None = None):
        self._task_counter += 1
        task_id = f"{self._task_counter:03d}"
        key = tool_call_id or tool_name
        self._task_ids[key] = task_id
        self._tool_names[key] = tool_name
        title = TOOL_DISPLAY_NAMES.get(tool_name, tool_name)
        self._stream.append(
            chunks=[TaskUpdateChunk(id=task_id, title=title, status="in_progress")]
        )

    def tool_completed(self, tool_call_id: str):
        task_id = self._task_ids.get(tool_call_id)
        tool_name = self._tool_names.get(tool_call_id, "")
        if task_id:
            title = TOOL_DISPLAY_NAMES.get(tool_name, tool_name)
            self._stream.append(
                chunks=[TaskUpdateChunk(id=task_id, title=title, status="complete")]
            )

    def tool_errored(self, tool_call_id: str):
        task_id = self._task_ids.get(tool_call_id)
        tool_name = self._tool_names.get(tool_call_id, "")
        if task_id:
            title = TOOL_DISPLAY_NAMES.get(tool_name, tool_name)
            self._stream.append(
                chunks=[TaskUpdateChunk(id=task_id, title=title, status="error")]
            )


def create_event_handler(plan: PlanStreamer):
    """Create a Pydantic AI event stream handler that bridges events to PlanStreamer."""

    async def handler(
        ctx: RunContext[CaseyDeps], events: AsyncIterable[AgentStreamEvent]
    ):
        async for event in events:
            if isinstance(event, FunctionToolCallEvent):
                plan.tool_started(event.part.tool_name, event.tool_call_id)
            elif isinstance(event, FunctionToolResultEvent):
                plan.tool_completed(event.tool_call_id)

    return handler
