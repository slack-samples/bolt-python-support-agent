import random

from agents import function_tool
from agents.run_context import RunContextWrapper

from agent.deps import CaseyDeps


@function_tool
async def create_support_ticket(
    wrapper: RunContextWrapper[CaseyDeps],
    title: str,
    description: str,
    priority: str,
    category: str,
) -> str:
    """Create a new IT support ticket for issues that require human follow-up.

    Use this tool when a user's issue cannot be resolved through knowledge base
    articles or automated tools, and needs to be escalated to the IT support team.

    Args:
        title: A concise title describing the issue.
        description: A detailed description of the problem and any troubleshooting already attempted.
        priority: The ticket priority level — one of 'low', 'medium', 'high', or 'critical'.
        category: The issue category — one of 'hardware', 'software', 'network', 'access', or 'other'.
    """
    ticket_id = f"INC-{random.randint(100000, 999999)}"

    return (
        f"Support ticket created successfully.\n"
        f"**Ticket ID:** {ticket_id}\n"
        f"**Title:** {title}\n"
        f"**Priority:** {priority}\n"
        f"**Category:** {category}\n"
        f"**Status:** Open\n"
        f"**Assigned to:** IT Support Queue\n\n"
        f"The IT team will review this ticket and follow up within the SLA for {priority} priority issues."
    )
