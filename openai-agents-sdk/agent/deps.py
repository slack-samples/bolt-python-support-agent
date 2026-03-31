from dataclasses import dataclass

from slack_sdk import WebClient


@dataclass
class CaseyDeps:
    client: WebClient
    user_id: str
    channel_id: str
    thread_ts: str
    message_ts: str
