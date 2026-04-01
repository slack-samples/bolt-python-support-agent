from agents import Agent, RunContextWrapper, RunHooks, Tool

from agent.deps import CaseyDeps
from slack_sdk.models.messages.chunk import TaskUpdateChunk
from slack_sdk.web.chat_stream import ChatStream

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

    def tool_started(self, tool_name: str, tool_call_id: str | None = None):
        self._task_counter += 1
        task_id = f"{self._task_counter:03d}"
        key = tool_call_id or tool_name
        self._task_ids[key] = task_id
        title = TOOL_DISPLAY_NAMES.get(tool_name, tool_name)
        self._stream.append(
            chunks=[TaskUpdateChunk(id=task_id, title=title, status="in_progress")]
        )

    def tool_completed(self, tool_name: str, tool_call_id: str | None = None):
        key = tool_call_id or tool_name
        task_id = self._task_ids.get(key)
        if task_id:
            title = TOOL_DISPLAY_NAMES.get(tool_name, tool_name)
            self._stream.append(
                chunks=[TaskUpdateChunk(id=task_id, title=title, status="complete")]
            )

    def tool_errored(self, tool_name: str, tool_call_id: str | None = None):
        key = tool_call_id or tool_name
        task_id = self._task_ids.get(key)
        if task_id:
            title = TOOL_DISPLAY_NAMES.get(tool_name, tool_name)
            self._stream.append(
                chunks=[TaskUpdateChunk(id=task_id, title=title, status="error")]
            )


class CaseyPlanHooks(RunHooks[CaseyDeps]):
    """OpenAI Agents SDK hooks that bridge tool lifecycle events to PlanStreamer."""

    def __init__(self, plan_streamer: PlanStreamer):
        self._plan = plan_streamer

    async def on_tool_start(
        self, context: RunContextWrapper[CaseyDeps], agent: Agent, tool: Tool
    ):
        self._plan.tool_started(tool.name)

    async def on_tool_end(
        self,
        context: RunContextWrapper[CaseyDeps],
        agent: Agent,
        tool: Tool,
        result: str,
    ):
        self._plan.tool_completed(tool.name)
