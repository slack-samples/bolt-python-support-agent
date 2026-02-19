# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Is

A monorepo containing three parallel implementations of **Casey**, an AI-powered IT helpdesk agent for Slack built with Bolt for Python. All implementations are functionally identical from the Slack user's perspective but use different AI agent frameworks:

- `pydantic-ai/` — Built with **Pydantic AI**
- `openai-agents-sdk/` — Built with **OpenAI Agents SDK**
- `claude-agent-sdk/` — Built with **Claude Agent SDK**

All tool data (knowledge base, tickets, password resets, system status, permissions) is hardcoded for demo purposes.

## Commands

All commands must be run from within the respective project directory (`pydantic-ai/`, `openai-agents-sdk/`, or `claude-agent-sdk/`).

```sh
# Run the app (requires .env with OPENAI_API_KEY or ANTHROPIC_API_KEY; Slack tokens optional with CLI)
slack run          # via Slack CLI
python3 app.py     # directly

# Lint and format (CI runs these on push to main and all PRs)
ruff check .
ruff format --check .

# Run tests
pytest
```

## Monorepo Structure

```
.github/              # Shared CI workflows and dependabot config
pydantic-ai/         # Pydantic AI implementation
openai-agents-sdk/   # OpenAI Agents SDK implementation
claude-agent-sdk/    # Claude Agent SDK implementation
```

CI runs ruff lint/format checks against all directories via a matrix strategy in `.github/workflows/ruff.yml`. Dependabot monitors `requirements.txt` in all directories independently.

## Architecture (shared across both implementations)

Three-layer design: **app.py** → **listeners/** → **agent/**

**Entry point (`app.py`)** initializes Bolt with Socket Mode and calls `register_listeners(app)`.

**Listeners** are organized by Slack platform feature:
- `listeners/events/` — `app_home_opened`, `app_mentioned`, `message_im`
- `listeners/actions/` — `category_buttons` (regex `^category_`), feedback handlers
- `listeners/views/` — `issue_submission` modal handler

Each sub-package has a `register(app)` function called from `listeners/__init__.py`.

**CaseyDeps** (`agent/deps.py`) is a dataclass carrying `client`, `user_id`, `channel_id`, `thread_ts`. Constructed in each listener handler and passed to the agent at runtime.

**Conversation history** (`conversation/store.py`) is a thread-safe in-memory dict keyed by `(channel_id, thread_ts)` with TTL-based cleanup. This enables multi-turn context.

**Handler flow** (DM, mention, modal submit): add `:eyes:` reaction → get history from store → run agent → post response in thread with feedback blocks → store updated messages.

## Key Differences Between Implementations

| Aspect | Pydantic AI | OpenAI Agents SDK | Claude Agent SDK |
|--------|-------------|-------------------|-----------------|
| Agent file | `agent/casey.py` | `agent/support_agent.py` | `agent/casey.py` |
| App type | `App` (sync) | `App` (sync) | `AsyncApp` (fully async) |
| Agent definition | `Agent(deps_type=CaseyDeps)` | `Agent[CaseyDeps](model="gpt-4o-mini")` | `ClaudeSDKClient` with `ClaudeAgentOptions` |
| Model config | Passed at runtime via `run_sync(model=DEFAULT_MODEL)` | Set directly on agent constructor | Managed by SDK (Claude models) |
| Tool definition | Plain async functions | `@function_tool` decorated functions | `@tool` decorated functions via MCP server |
| Tool context param | `RunContext[CaseyDeps]` | `RunContextWrapper[CaseyDeps]` | `args` dict (no context param) |
| Execution | `casey_agent.run_sync(text, model=..., deps=..., message_history=...)` | `Runner.run_sync(casey_agent, input=..., context=...)` | `await run_casey_agent(text, session_id=...)` |
| Result output | `result.output` | `result.final_output` | `response_text` from collected `TextBlock.text` |
| Conversation history | `list[ModelMessage]` stored locally | `list` stored locally | Session-based via `resume` (server-side) |
| API key env var | `OPENAI_API_KEY` | `OPENAI_API_KEY` | `ANTHROPIC_API_KEY` |
| Feedback blocks | Native `FeedbackButtonsElement` | Native `FeedbackButtonsElement` | Native `FeedbackButtonsElement` |
