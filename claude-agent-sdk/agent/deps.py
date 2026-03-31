from dataclasses import dataclass

from slack_sdk.web.async_client import AsyncWebClient


@dataclass
class CaseyDeps:
    client: AsyncWebClient
    user_id: str
    channel_id: str
    thread_ts: str
    message_ts: str
