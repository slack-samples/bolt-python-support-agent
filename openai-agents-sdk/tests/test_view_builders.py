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
    """Default args (Socket Mode) — shows disconnected status with learn-more link."""
    view = build_app_home_view()

    assert view["type"] == "home"

    # Find the actions block containing category buttons
    actions_block = next(b for b in view["blocks"] if b["type"] == "actions")
    assert len(actions_block["elements"]) == len(CATEGORIES)

    # Shows MCP status as disconnected with learn-more link
    section_texts = [
        b["text"]["text"] for b in view["blocks"] if b["type"] == "section"
    ]
    mcp_section = next(t for t in section_texts if "Slack MCP Server" in t)
    assert "disconnected" in mcp_section
    assert "Learn how to enable" in mcp_section


def test_build_app_home_view_connect():
    """install_url provided — shows disconnected status with install link."""
    view = build_app_home_view(install_url="https://example.com/slack/install")

    section_texts = [
        b["text"]["text"] for b in view["blocks"] if b["type"] == "section"
    ]
    mcp_section = next(t for t in section_texts if "Slack MCP Server" in t)
    assert "disconnected" in mcp_section
    assert "https://example.com/slack/install" in mcp_section


def test_build_app_home_view_connected():
    """is_connected=True — shows connected status."""
    view = build_app_home_view(is_connected=True)

    section_texts = [
        b["text"]["text"] for b in view["blocks"] if b["type"] == "section"
    ]
    mcp_section = next(t for t in section_texts if "Slack MCP Server" in t)
    assert "connected" in mcp_section
