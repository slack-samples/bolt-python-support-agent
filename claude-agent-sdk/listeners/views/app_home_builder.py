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


def build_app_home_view(is_connected: bool = False) -> dict:
    """Build the App Home Block Kit view with category buttons."""
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
                        ":white_check_mark: *Your Slack account is connected.*\n"
                        "Casey has access to search messages, read channels, and more."
                    ),
                },
                "accessory": {
                    "type": "button",
                    "text": {"type": "plain_text", "text": "Disconnect"},
                    "action_id": "disconnect_account",
                    "style": "danger",
                },
            }
        )
    else:
        blocks.append(
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": (
                        ":electric_plug: *Connect your Slack account*\n"
                        "Unlock full functionality including searching messages, "
                        "reading channels, and more."
                    ),
                },
                "accessory": {
                    "type": "button",
                    "text": {"type": "plain_text", "text": "Connect"},
                    "action_id": "connect_account",
                    "style": "primary",
                },
            }
        )

    return {
        "type": "home",
        "blocks": blocks,
    }
