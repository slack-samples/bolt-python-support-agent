from agents import function_tool
from agents.run_context import RunContextWrapper

from agent.deps import CaseyDeps

SYSTEM_STATUSES = {
    "email": {
        "name": "Email (Exchange Online)",
        "status": "operational",
        "details": "All email services running normally. Last incident resolved 3 days ago.",
    },
    "vpn": {
        "name": "Corporate VPN",
        "status": "degraded",
        "details": "Intermittent connectivity issues reported on the US-East gateway. Engineering is investigating. ETA for resolution: 2 hours.",
    },
    "jira": {
        "name": "Jira",
        "status": "operational",
        "details": "All project management services running normally.",
    },
    "confluence": {
        "name": "Confluence",
        "status": "operational",
        "details": "Wiki and documentation services running normally.",
    },
    "slack": {
        "name": "Slack",
        "status": "operational",
        "details": "All messaging services running normally.",
    },
    "github": {
        "name": "GitHub Enterprise",
        "status": "operational",
        "details": "All code repository and CI/CD services running normally.",
    },
    "sso": {
        "name": "Single Sign-On (SSO)",
        "status": "operational",
        "details": "Authentication services running normally.",
    },
    "network": {
        "name": "Corporate Network",
        "status": "operational",
        "details": "All office networks operating at full capacity.",
    },
    "erp": {
        "name": "ERP System",
        "status": "maintenance",
        "details": "Scheduled maintenance window active. Service will be restored by 6:00 AM UTC tomorrow.",
    },
}


@function_tool
async def check_system_status(
    wrapper: RunContextWrapper[CaseyDeps], system_name: str
) -> str:
    """Check the current operational status of a company system or service.

    Use this tool when a user asks about outages, system availability, or
    whether a specific service is currently working.

    Args:
        system_name: The name of the system to check (e.g., 'vpn', 'email', 'jira', 'github', 'sso').
    """
    system_lower = system_name.lower()

    for key, info in SYSTEM_STATUSES.items():
        if key in system_lower or system_lower in info["name"].lower():
            status_emoji = {
                "operational": ":large_green_circle:",
                "degraded": ":large_yellow_circle:",
                "outage": ":red_circle:",
                "maintenance": ":wrench:",
            }.get(info["status"], ":white_circle:")

            return (
                f"**{info['name']}** {status_emoji} `{info['status'].upper()}`\n"
                f"{info['details']}"
            )

    available = ", ".join(sorted(SYSTEM_STATUSES.keys()))
    return (
        f"System '{system_name}' not found in monitoring. "
        f"Available systems: {available}. "
        f"If you need status for a different system, try a more specific name."
    )
