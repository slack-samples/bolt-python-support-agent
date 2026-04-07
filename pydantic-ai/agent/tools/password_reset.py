from pydantic_ai import RunContext

from agent.deps import CaseyDeps


async def trigger_password_reset(ctx: RunContext[CaseyDeps], target_user: str) -> str:
    """Trigger a password reset for a specified user account.

    Use this tool when a user requests a password reset for their own account
    or reports being locked out. The reset link will be sent to their registered
    email address.

    Before calling this tool, look up the user's email address using available
    Slack tools if possible, rather than asking the user for it.

    Args:
        ctx: The run context with dependencies.
        target_user: The username or email of the user whose password should be reset.
    """
    return (
        f"Password reset initiated for **{target_user}**.\n\n"
        f"A reset link has been emailed to **{target_user}**. "
        f"The link will expire in 30 minutes.\n\n"
        f"_If the user doesn't receive the email within 5 minutes, "
        f"ask them to check their spam folder or verify their registered email address._"
    )
