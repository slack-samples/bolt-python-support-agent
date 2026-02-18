# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Is

Casey is an AI-powered IT helpdesk agent for Slack, built with Bolt for Python and Pydantic AI. It uses simulated tools (knowledge base, ticket creation, password reset, system status, permissions lookup) to demonstrate an agentic IT support workflow. All tool data is hardcoded for demo purposes.

## Commands

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

## Architecture

Three-layer design: **app.py** → **listeners/** → **agent/**

**Entry point (`app.py`)** initializes Bolt with Socket Mode and calls `register_listeners(app)`.

**Listeners** are organized by Slack platform feature:
- `listeners/events/` — `app_home_opened`, `app_mentioned`, `message_im`
- `listeners/actions/` — `category_buttons` (regex `^category_`), `feedback_good`, `feedback_bad`
- `listeners/views/` — `issue_submission` modal handler

Each sub-package has a `register(app)` function called from `listeners/__init__.py`.

**Agent (`agent/casey.py`)** is a Pydantic AI `Agent` with `deps_type=CaseyDeps`. The model is **not** set on the agent (to avoid import-time OpenAI client creation); instead `DEFAULT_MODEL` (`openai:gpt-4o-mini`) is passed at each `run_sync()` call site. Tools are passed via the `tools=[]` constructor parameter (not decorators) so each tool lives in its own file under `agent/tools/`.

**CaseyDeps** (`agent/deps.py`) is a dataclass carrying `client`, `user_id`, `channel_id`, `thread_ts`. It's constructed in each listener handler and passed as `deps=` to `run_sync()`.

**Conversation history** (`conversation/store.py`) is an in-memory dict keyed by `(channel_id, thread_ts)` storing `list[ModelMessage]` from Pydantic AI. This is what enables multi-turn context. The singleton `conversation_store` is imported from `conversation/`.

## Key Patterns

- All three message handlers (DM, mention, modal submit) follow the same flow: add :eyes: reaction → get history from store → `casey_agent.run_sync(text, model=DEFAULT_MODEL, deps=deps, message_history=history)` → post `result.output` in thread with feedback blocks → store `result.all_messages()`.
- Emoji/reaction logic is in the handlers, not the agent. Resolution detection checks `result.output` against a hardcoded phrase list.
- View builders (`app_home_builder.py`, `modal_builder.py`, `feedback_block.py`) return raw dicts or Block Kit objects, not views themselves. The handlers call `client.views_publish()` or `client.views_open()`.
- The `message_im` handler filters out bot messages (`event.bot_id`) and subtypes to avoid self-reply loops.
