from pydantic_ai import RunContext

from agent.deps import CaseyDeps


async def lookup_user_permissions(
    ctx: RunContext[CaseyDeps], target_user: str, system: str
) -> str:
    """Look up a user's access permissions and group memberships for a given system.

    Use this tool when a user asks about their access level, group memberships,
    or whether they have permission to use a specific system or resource.

    Args:
        ctx: The run context with dependencies.
        target_user: The username or email of the user to look up.
        system: The system or resource to check permissions for (e.g., 'github', 'jira', 'aws').
    """
    return (
        f"*Permissions for {target_user} on {system}:*\n\n"
        f"*Groups:* `{system}-users`, `{system}-readonly`\n"
        f"*Access Level:* Standard User\n"
        f"*Last Login:* 2 hours ago\n"
        f"*Account Status:* Active\n"
        f"*MFA Enabled:* Yes\n\n"
        f"_To request elevated access, the user's manager must submit an access request "
        f"through the IT portal._"
    )
