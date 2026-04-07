from claude_agent_sdk import tool


@tool(
    name="trigger_password_reset",
    description=(
        "Trigger a password reset for a specified user account. "
        "Use this tool when a user requests a password reset for their own account "
        "or reports being locked out. The reset link will be sent to their registered "
        "email address. Before calling this tool, look up the user's email address "
        "using available Slack tools if possible, rather than asking the user for it."
    ),
    input_schema={"target_user": str},
)
async def trigger_password_reset_tool(args):
    """Trigger a password reset for a specified user account."""
    target_user = args["target_user"]

    text = (
        f"Password reset initiated for **{target_user}**.\n\n"
        f"A reset link has been sent to **{target_user}@acme.com**. "
        f"The link will expire in 30 minutes.\n\n"
        f"_If the user doesn't receive the email within 5 minutes, "
        f"ask them to check their spam folder or verify their registered email address._"
    )

    return {"content": [{"type": "text", "text": text}]}
