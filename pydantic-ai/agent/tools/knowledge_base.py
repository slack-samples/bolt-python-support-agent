from pydantic_ai import RunContext

from agent.deps import CaseyDeps

KB_ARTICLES = {
    "vpn": {
        "title": "VPN Connection Troubleshooting",
        "content": (
            "1. Ensure you're connected to the internet\n"
            "2. Restart the VPN client application\n"
            "3. Try connecting to a different VPN server region\n"
            "4. Clear VPN client cache: Settings > Advanced > Clear Cache\n"
            "5. If still failing, uninstall and reinstall the VPN client from the Software Center"
        ),
        "article_id": "KB-1001",
    },
    "email": {
        "title": "Email Configuration and Common Issues",
        "content": (
            "1. Verify your email credentials at mail.company.com/settings\n"
            "2. For Outlook sync issues, remove and re-add the account\n"
            "3. Check mailbox storage quota in Settings > Storage\n"
            "4. For mobile email setup, use ActiveSync with server mail.company.com\n"
            "5. Two-factor authentication must be enabled for email access"
        ),
        "article_id": "KB-1002",
    },
    "wifi": {
        "title": "Office Wi-Fi Connection Guide",
        "content": (
            "1. Connect to 'CorpNet-Secure' (not 'CorpNet-Guest') for internal access\n"
            "2. Use your network credentials (same as laptop login)\n"
            "3. If prompted for a certificate, click 'Trust' or 'Accept'\n"
            "4. Forget and rejoin the network if experiencing intermittent drops\n"
            "5. Guest network: 'CorpNet-Guest', password rotates weekly (check lobby display)"
        ),
        "article_id": "KB-1003",
    },
    "software": {
        "title": "Software Installation and Requests",
        "content": (
            "1. Approved software can be installed from the Software Center app\n"
            "2. For software not in the catalog, submit a request via the IT portal\n"
            "3. License requests typically take 2-3 business days for approval\n"
            "4. Admin rights are not granted for standard installations\n"
            "5. For developer tools, request access through your team lead"
        ),
        "article_id": "KB-1004",
    },
    "printer": {
        "title": "Printer Setup and Troubleshooting",
        "content": (
            "1. Add network printers via Settings > Printers > Add > search 'CorpPrint'\n"
            "2. Default printer drivers are installed automatically\n"
            "3. For print queue issues, restart the Print Spooler service\n"
            "4. Color printing requires manager approval code\n"
            "5. Secure print: Use your badge at the printer to release jobs"
        ),
        "article_id": "KB-1005",
    },
    "password": {
        "title": "Password Policy and Reset Guide",
        "content": (
            "1. Passwords must be at least 12 characters with uppercase, lowercase, number, and symbol\n"
            "2. Passwords expire every 90 days\n"
            "3. Self-service reset available at password.company.com\n"
            "4. Account locks after 5 failed attempts (auto-unlocks after 30 minutes)\n"
            "5. For immediate unlock, contact IT helpdesk or use Casey's password reset tool"
        ),
        "article_id": "KB-1006",
    },
    "hardware": {
        "title": "Hardware Requests and Replacements",
        "content": (
            "1. Standard hardware refresh cycle is every 3 years\n"
            "2. Submit hardware requests through the IT portal under 'Equipment'\n"
            "3. Emergency replacements available for broken/lost devices\n"
            "4. Peripheral requests (monitors, keyboards) approved by direct manager\n"
            "5. All hardware must be returned upon offboarding"
        ),
        "article_id": "KB-1007",
    },
    "security": {
        "title": "Security Best Practices",
        "content": (
            "1. Never share your credentials or write passwords on sticky notes\n"
            "2. Report suspicious emails to phishing@company.com\n"
            "3. Enable two-factor authentication on all supported systems\n"
            "4. Lock your workstation when stepping away (Win+L or Cmd+Ctrl+Q)\n"
            "5. Do not connect personal USB drives to company devices"
        ),
        "article_id": "KB-1008",
    },
}


async def search_knowledge_base(ctx: RunContext[CaseyDeps], query: str) -> str:
    """Search the IT knowledge base for articles matching the given query.

    Use this tool when users ask about common IT topics like VPN, email, Wi-Fi,
    software installation, printers, passwords, hardware, or security.

    Args:
        ctx: The run context with dependencies.
        query: The search query describing the user's issue or topic.
    """
    query_lower = query.lower()
    matches = []

    for keyword, article in KB_ARTICLES.items():
        if keyword in query_lower or any(
            word in query_lower for word in article["title"].lower().split()
        ):
            matches.append(article)

    if not matches:
        return "No knowledge base articles found matching the query. Consider creating a support ticket for further assistance."

    results = []
    for article in matches:
        results.append(
            f"**{article['title']}** ({article['article_id']})\n{article['content']}"
        )

    return "\n\n---\n\n".join(results)
