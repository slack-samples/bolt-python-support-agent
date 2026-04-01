# Casey: IT Helpdesk Agent (Bolt for Python and OpenAI Agents SDK)

Meet Casey (it/this/that) — an AI-powered IT helpdesk agent that lives in Slack. Casey can troubleshoot common issues, search knowledge base articles, reset passwords, check system status, and create support tickets, all without leaving the conversation.

Built with [Bolt for Python](https://docs.slack.dev/tools/bolt-python/) and [OpenAI Agents SDK](https://openai.github.io/openai-agents-python/) using models from [OpenAI](https://openai.com).

## App Overview

Casey gives your team instant IT support through three entry points:

* **App Home** — Users open Casey's Home tab and choose from common issue categories (Password Reset, Access Request, Software Help, Network Issues, Something Else). A modal collects details, then Casey starts a DM thread with a resolution.
* **Direct Messages** — Users message Casey directly to describe any IT issue. Casey responds in-thread, maintaining context across follow-ups.
* **Channel @mentions** — Users mention `@Casey` in any channel to get help without leaving the conversation.

Casey uses five simulated tools to assist users:

* **Knowledge Base Search** — Finds relevant articles for common topics like VPN, email, Wi-Fi, printers, and more.
* **Support Ticket Creation** — Creates a tracked ticket when issues need human follow-up.
* **Password Reset** — Triggers a password reset and confirms the action.
* **System Status Check** — Reports the operational status of company systems.
* **User Permissions Lookup** — Shows access levels and group memberships.

> **Note:** All tools return simulated data for demonstration purposes. In a production app, these would connect to your actual IT systems.

## Setup

Before getting started, make sure you have a development workspace where you have permissions to install apps.

### Developer Program

Join the [Slack Developer Program](https://api.slack.com/developer-program) for exclusive access to sandbox environments for building and testing your apps, tooling, and resources created to help you build and grow.

### Create the Slack app

<details><summary><strong>Using Slack CLI</strong></summary>

Install the latest version of the Slack CLI for your operating system:

- [Slack CLI for macOS & Linux](https://docs.slack.dev/tools/slack-cli/guides/installing-the-slack-cli-for-mac-and-linux/)
- [Slack CLI for Windows](https://docs.slack.dev/tools/slack-cli/guides/installing-the-slack-cli-for-windows/)

You'll also need to log in if this is your first time using the Slack CLI.

```sh
slack login
```

#### Initializing the project

```sh
slack create my-casey-agent --template slack-samples/bolt-python-support-agent
cd my-casey-agent
```

</details>

<details><summary><strong>Using App Settings</strong></summary>

#### Create Your Slack App

1. Open [https://api.slack.com/apps/new](https://api.slack.com/apps/new) and choose "From an app manifest"
2. Choose the workspace you want to install the application to
3. Copy the contents of [manifest.json](./manifest.json) into the text box that says `*Paste your manifest code here*` (within the JSON tab) and click _Next_
4. Review the configuration and click _Create_
5. Click _Install to Workspace_ and _Allow_ on the screen that follows. You'll then be redirected to the App Configuration dashboard.

#### Environment Variables

Before you can run the app, you'll need to store some environment variables.

1. Rename `.env.sample` to `.env`.
2. Open your apps setting page from [this list](https://api.slack.com/apps), click _OAuth & Permissions_ in the left hand menu, then copy the _Bot User OAuth Token_ into your `.env` file under `SLACK_BOT_TOKEN`.

```sh
SLACK_BOT_TOKEN=YOUR_SLACK_BOT_TOKEN
```

3. Click _Basic Information_ from the left hand menu and follow the steps in the _App-Level Tokens_ section to create an app-level token with the `connections:write` scope. Copy that token into your `.env` as `SLACK_APP_TOKEN`.

```sh
SLACK_APP_TOKEN=YOUR_SLACK_APP_TOKEN
```

#### Initializing the project

```sh
git clone https://github.com/slack-samples/bolt-python-support-agent.git my-casey-agent
cd my-casey-agent
```

</details>

### Setup your python virtual environment

```sh
python3 -m venv .venv
source .venv/bin/activate  # for Windows OS, .\.venv\Scripts\Activate instead should work
```

#### Install dependencies

```sh
pip install -r requirements.txt
```

## Providers

### OpenAI Setup

This app uses OpenAI's `gpt-4.1-mini` model through the OpenAI Agents SDK.

1. Create an API key from your [OpenAI dashboard](https://platform.openai.com/api-keys).
1. Rename `.env.sample` to `.env`.
3. Save the OpenAI API key to `.env`:

```sh
OPENAI_API_KEY=YOUR_OPENAI_API_KEY
```

## Development

### Starting the app

<details><summary><strong>Using the Slack CLI</strong></summary>

#### Slack CLI

```sh
slack run
```
</details>

<details><summary><strong>Using the Terminal</strong></summary>

#### Terminal

```sh
python3 app.py
```

</details>

### Using the App

Once Casey is running, there are three ways to interact:

**App Home** — Open Casey in Slack and click the _Home_ tab. You'll see five category buttons. Click one to open a modal, describe your issue, and submit. Casey will start a DM thread with you containing a diagnosis and next steps.

**Direct Messages** — Open a DM with Casey and describe your issue. Casey will react with :eyes: while processing, then reply in a thread. Send follow-up messages in the same thread and Casey will maintain the full conversation context.

**Channel @mentions** — In any channel where Casey has been added, type `@Casey` followed by your issue. Casey responds in a thread so the channel stays clean.

Casey will add a :white_check_mark: reaction when it believes an issue has been resolved, and occasionally adds a contextual emoji reaction to keep things friendly.

### Linting

```sh
# Run ruff check from root directory for linting
ruff check

# Run ruff format from root directory for code formatting
ruff format
```

## Project Structure

### `manifest.json`

`manifest.json` is a configuration for Slack apps. With a manifest, you can create an app with a pre-defined configuration, or adjust the configuration of an existing app.

### `app.py`

`app.py` is the entry point for the application and is the file you'll run to start the server. This project aims to keep this file as thin as possible, primarily using it as a way to route inbound requests.

### `/listeners`

Every incoming request is routed to a "listener". This directory groups each listener based on the Slack Platform feature used.

**`/listeners/events`** — Handles incoming events:

- `app_home_opened.py` — Publishes the App Home view with category buttons.
- `app_mentioned.py` — Responds to `@Casey` mentions in channels.
- `message.py` — Responds to direct messages from users.

**`/listeners/actions`** — Handles interactive components:

- `category_buttons.py` — Opens the issue submission modal when a category button is clicked.
- `feedback.py` — Handles thumbs up/down feedback on Casey's responses.

**`/listeners/views`** — Handles view submissions and builds Block Kit views:

- `issue_modal.py` — Processes modal submissions, starts a DM thread, and runs the agent.
- `app_home_builder.py` — Constructs the App Home Block Kit view.
- `modal_builder.py` — Constructs the issue submission modal.
- `feedback_block.py` — Creates the feedback button block attached to responses.

### `/agent`

The `support_agent.py` file defines the OpenAI Agents SDK Agent with a system prompt, personality, and tool configuration.

The `deps.py` file defines the `CaseyDeps` dataclass passed to the agent at runtime, providing access to the Slack client and conversation context.

The `tools` directory contains five IT helpdesk tools that the agent can call during a conversation.

### `/thread_context`

The `store.py` file implements a thread-safe in-memory conversation history store, keyed by channel and thread. This enables multi-turn conversations where Casey remembers previous context within a thread.
