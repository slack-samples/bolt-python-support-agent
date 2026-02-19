from claude_agent_sdk import tool


@tool(
    name="lookup_user_permissions",
    description=(
        "Look up a user's access permissions and group memberships for a given system. "
        "Use this tool when a user asks about their access level, group memberships, "
        "or whether they have permission to use a specific system or resource."
    ),
    input_schema={
        "type": "object",
        "properties": {
            "target_user": {
                "type": "string",
                "description": "The username or email of the user to look up.",
            },
            "system": {
                "type": "string",
                "description": "The system or resource to check permissions for (e.g., 'github', 'jira', 'aws').",
            },
        },
        "required": ["target_user", "system"],
    },
)
async def lookup_user_permissions_tool(args):
    """Look up a user's access permissions and group memberships for a given system."""
    target_user = args["target_user"]
    system = args["system"]

    text = (
        f"**Permissions for {target_user} on {system}:**\n\n"
        f"**Groups:** `{system}-users`, `{system}-readonly`\n"
        f"**Access Level:** Standard User\n"
        f"**Last Login:** 2 hours ago\n"
        f"**Account Status:** Active\n"
        f"**MFA Enabled:** Yes\n\n"
        f"_To request elevated access, the user's manager must submit an access request "
        f"through the IT portal._"
    )

    return {"content": [{"type": "text", "text": text}]}
