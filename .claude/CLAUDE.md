# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Is

A monorepo containing two parallel implementations of **Casey**, an AI-powered IT helpdesk agent for Slack built with Bolt for Python. Both implementations are functionally identical from the Slack user's perspective but use different AI agent frameworks:

- `pydantic-ai/` — Built with **Pydantic AI**
- `openai-agents-sdk/` — Built with **OpenAI Agents SDK**

All tool data (knowledge base, tickets, password resets, system status, permissions) is hardcoded for demo purposes.

## Commands

All commands must be run from within the respective project directory (`pydantic-ai/` or `openai-agents-sdk/`).

```sh
# Run the app (requires .env with OPENAI_API_KEY; Slack tokens optional with CLI)
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
```

CI runs ruff lint/format checks against both directories via a matrix strategy in `.github/workflows/ruff.yml`. Dependabot monitors `requirements.txt` in both directories independently.

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

| Aspect | Pydantic AI | OpenAI Agents SDK |
|--------|-------------|-------------------|
| Agent file | `agent/casey.py` | `agent/support_agent.py` |
| Agent definition | `Agent(deps_type=CaseyDeps)` | `Agent[CaseyDeps](model="gpt-4o-mini")` |
| Model config | Passed at runtime via `run_sync(model=DEFAULT_MODEL)` | Set directly on agent constructor |
| Tool definition | Plain async functions | `@function_tool` decorated functions |
| Tool context param | `RunContext[CaseyDeps]` | `RunContextWrapper[CaseyDeps]` |
| Execution | `casey_agent.run_sync(text, model=..., deps=..., message_history=...)` | `Runner.run_sync(casey_agent, input=..., context=...)` |
| Result output | `result.output` | `result.final_output` |
| Result messages | `result.all_messages()` | `result.to_input_list()` |
| History type | `list[ModelMessage]` (framework-native) | `list` (generic, manually constructed) |
| Feedback blocks | Native `FeedbackButtonsElement` | Custom `ButtonElement` pair |
