from listeners.views.app_home_builder import CATEGORIES


def build_issue_modal(category: str) -> dict:
    """Build the issue submission modal pre-filled with the selected category.

    Args:
        category: The pre-selected category value from the button click.
    """
    category_options = [
        {
            "text": {"type": "plain_text", "text": cat["value"], "emoji": True},
            "value": cat["value"],
        }
        for cat in CATEGORIES
    ]

    initial_option = next(
        (opt for opt in category_options if opt["value"] == category),
        category_options[0],
    )

    return {
        "type": "modal",
        "callback_id": "issue_submission",
        "title": {"type": "plain_text", "text": "Submit an Issue"},
        "submit": {"type": "plain_text", "text": "Submit"},
        "close": {"type": "plain_text", "text": "Cancel"},
        "blocks": [
            {
                "type": "input",
                "block_id": "category_block",
                "element": {
                    "type": "static_select",
                    "action_id": "category_select",
                    "placeholder": {
                        "type": "plain_text",
                        "text": "Select a category",
                    },
                    "options": category_options,
                    "initial_option": initial_option,
                },
                "label": {"type": "plain_text", "text": "Category"},
            },
            {
                "type": "input",
                "block_id": "description_block",
                "element": {
                    "type": "plain_text_input",
                    "action_id": "description_input",
                    "multiline": True,
                    "placeholder": {
                        "type": "plain_text",
                        "text": "Describe your issue in detail...",
                    },
                },
                "label": {"type": "plain_text", "text": "Description"},
            },
        ],
    }
