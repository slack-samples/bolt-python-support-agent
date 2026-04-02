from listeners.views.app_home_builder import CATEGORIES, build_app_home_view
from listeners.views.feedback_builder import build_feedback_blocks
from listeners.views.issue_modal_builder import build_issue_modal


def test_build_issue_modal():
    modal = build_issue_modal("Password Reset")

    assert modal["type"] == "modal"
    assert modal["callback_id"] == "issue_submission"

    # The initial option should match the selected category
    category_block = modal["blocks"][0]
    initial = category_block["element"]["initial_option"]
    assert initial["value"] == "Password Reset"


def test_build_feedback_blocks():
    blocks = build_feedback_blocks()

    assert len(blocks) > 0
    # The block should contain a feedback action
    block_dict = blocks[0].to_dict()
    action_ids = [e["action_id"] for e in block_dict["elements"]]
    assert "feedback" in action_ids


def test_build_app_home_view_default():
    """Default args (app.py mode) — no OAuth section."""
    view = build_app_home_view()

    assert view["type"] == "home"

    # Find the actions block containing category buttons
    actions_block = next(b for b in view["blocks"] if b["type"] == "actions")
    assert len(actions_block["elements"]) == len(CATEGORIES)

    # No connect or disconnect buttons
    section_blocks = [b for b in view["blocks"] if b["type"] == "section"]
    accessory_actions = [
        b["accessory"]["action_id"] for b in section_blocks if "accessory" in b
    ]
    assert "connect_account" not in accessory_actions
    assert "disconnect_account" not in accessory_actions


def test_build_app_home_view_connect():
    """authorize_url provided — shows Connect URL button."""
    view = build_app_home_view(authorize_url="https://example.com/oauth")

    section_blocks = [b for b in view["blocks"] if b["type"] == "section"]
    connect_section = next(
        b
        for b in section_blocks
        if b.get("accessory", {}).get("action_id") == "connect_account"
    )
    assert connect_section["accessory"]["url"] == "https://example.com/oauth"


def test_build_app_home_view_disconnect():
    """is_connected=True — shows Disconnect button."""
    view = build_app_home_view(is_connected=True)

    section_blocks = [b for b in view["blocks"] if b["type"] == "section"]
    disconnect_section = next(
        b
        for b in section_blocks
        if b.get("accessory", {}).get("action_id") == "disconnect_account"
    )
    assert disconnect_section["accessory"]["style"] == "danger"
