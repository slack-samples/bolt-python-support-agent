import random

from claude_agent_sdk import tool


@tool(
    name="create_support_ticket",
    description=(
        "Create a new IT support ticket for issues that require human follow-up. "
        "Use this tool when a user's issue cannot be resolved through knowledge base "
        "articles or automated tools, and needs to be escalated to the IT support team."
    ),
    input_schema={
        "type": "object",
        "properties": {
            "title": {
                "type": "string",
                "description": "A concise title describing the issue.",
            },
            "description": {
                "type": "string",
                "description": "A detailed description of the problem and any troubleshooting already attempted.",
            },
            "priority": {
                "type": "string",
                "description": "The ticket priority level.",
                "enum": ["low", "medium", "high", "critical"],
            },
            "category": {
                "type": "string",
                "description": "The issue category.",
                "enum": ["hardware", "software", "network", "access", "other"],
            },
        },
        "required": ["title", "description", "priority", "category"],
    },
)
async def create_support_ticket_tool(args):
    """Create a new IT support ticket for issues that require human follow-up."""
    title = args["title"]
    priority = args["priority"]
    category = args["category"]

    ticket_id = f"INC-{random.randint(100000, 999999)}"

    text = (
        f"Support ticket created successfully.\n"
        f"**Ticket ID:** {ticket_id}\n"
        f"**Title:** {title}\n"
        f"**Priority:** {priority}\n"
        f"**Category:** {category}\n"
        f"**Status:** Open\n"
        f"**Assigned to:** IT Support Queue\n\n"
        f"The IT team will review this ticket and follow up within the SLA for {priority} priority issues."
    )

    return {"content": [{"type": "text", "text": text}]}
