# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

See the root `../.claude/CLAUDE.md` for monorepo-wide architecture, commands, and a comparison of the two implementations.

## Pydantic AI Specifics

**Agent (`agent/casey.py`)** is a Pydantic AI `Agent` with `deps_type=CaseyDeps`. The model is **not** set on the agent (to avoid import-time OpenAI client creation); instead `DEFAULT_MODEL` (`openai:gpt-5-nano`) is passed at each `run_sync()` call site. Tools are passed via the `tools=[]` constructor parameter (not decorators) so each tool lives in its own file under `agent/tools/`.

**Conversation history** stores `list[ModelMessage]` from Pydantic AI and is passed directly as `message_history=` to `run_sync()`.

**Feedback blocks** use the native `FeedbackButtonsElement` from `slack_sdk.models.blocks`. A single `feedback` action ID is registered.

The `message_im` handler only adds the `:eyes:` reaction on the first message in a thread (`if not event.get("thread_ts")`).
