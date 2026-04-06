CATEGORIES = [
    {
        "action_id": "category_password_reset",
        "text": ":closed_lock_with_key: Password Reset",
        "value": "Password Reset",
    },
    {
        "action_id": "category_access_request",
        "text": ":key: Access Request",
        "value": "Access Request",
    },
    {
        "action_id": "category_software_help",
        "text": ":computer: Software Help",
        "value": "Software Help",
    },
    {
        "action_id": "category_network_issues",
        "text": ":globe_with_meridians: Network Issues",
        "value": "Network Issues",
    },
    {
        "action_id": "category_something_else",
        "text": ":speech_balloon: Something Else",
        "value": "Something Else",
    },
]


def build_app_home_view(
    authorize_url: str | None = None, is_connected: bool = False
) -> dict:
    """Build the App Home Block Kit view with category buttons.

    Args:
        authorize_url: OAuth authorize URL. When provided, the user has not
            connected and will see a "Connect" URL button.
        is_connected: When ``True``, the user is connected and will see a
            "Disconnect" action button. When both params are default, the
            OAuth section is hidden (app.py mode).
    """
    blocks = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": "Hey there :wave: I'm Casey, your IT helpdesk agent.",
            },
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": (
                    "I can help you troubleshoot technical issues, reset passwords, "
                    "check system status, and create support tickets.\n\n"
                    "*Choose a category below to get started*, or send me a direct message anytime."
                ),
            },
        },
        {"type": "divider"},
        {
            "type": "actions",
            "elements": [
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": cat["text"],
                        "emoji": True,
                    },
                    "action_id": cat["action_id"],
                    "value": cat["value"],
                }
                for cat in CATEGORIES
            ],
        },
        {"type": "divider"},
        {
            "type": "context",
            "elements": [
                {
                    "type": "mrkdwn",
                    "text": "You can also mention me in any channel with `@Casey` or send me a DM.",
                }
            ],
        },
        {"type": "divider"},
    ]

    if is_connected:
        blocks.append(
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": (
                        "🟢 *Slack MCP Server is connected.*\n"
                        "Casey has access to search messages, read channels, and more."
                    ),
                },
            }
        )
    elif authorize_url:
        blocks.append(
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"🔴 *Slack MCP Server is disconnected.* <{authorize_url}|Connect now.>",
                },
            }
        )

    return {
        "type": "home",
        "blocks": blocks,
    }
