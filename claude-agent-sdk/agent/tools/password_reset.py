from claude_agent_sdk import tool


@tool(
    name="trigger_password_reset",
    description=(
        "Trigger a password reset for a specified user account. "
        "Use this tool when a user requests a password reset for their own account "
        "or reports being locked out. The reset link will be sent to their registered "
        "email address. "
        "IMPORTANT: You need the user's email address for target_user. "
        "First, try to look up the user's Slack profile to get their email address. "
        "If the lookup fails or does not return an email, ask the user for their email address. "
        "Never guess or assume — you must either look it up or ask for it."
    ),
    input_schema={"target_user": str},
)
async def trigger_password_reset_tool(args):
    """Trigger a password reset for a specified user account."""
    target_user = args["target_user"]

    text = (
        f"Password reset initiated for **{target_user}**.\n\n"
        f"A reset link has been emailed to **{target_user}**. "
        f"The link will expire in 30 minutes.\n\n"
        f"_If the user doesn't receive the email within 5 minutes, "
        f"ask them to check their spam folder or verify their registered email address._"
    )

    return {"content": [{"type": "text", "text": text}]}
