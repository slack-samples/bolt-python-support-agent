# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

See the root `../.claude/CLAUDE.md` for monorepo-wide architecture, commands, and a comparison of the two implementations.

## OpenAI Agents SDK Specifics

**Agent (`agent/support_agent.py`)** is an `Agent[CaseyDeps]` with the model set directly on the agent (`model="gpt-4o-mini"`). Tools are `@function_tool`-decorated async functions, each in its own file under `agent/tools/`. Execution uses `Runner.run_sync(casey_agent, input=..., context=deps)`.

**Conversation history** is stored as a generic `list` and must be manually combined with new user input before passing to `Runner.run_sync()`: `input_items = history + [{"role": "user", "content": text}]`. After execution, `result.to_input_list()` is stored back.

**Feedback blocks** use custom `ButtonElement` pairs inside an `ActionsBlock`, with separate `feedback_good` and `feedback_bad` action IDs. The `create_feedback_block(thread_ts)` function takes a timestamp to generate a unique `block_id`.

The `message_im` handler adds the `:eyes:` reaction on every message (including thread replies).
