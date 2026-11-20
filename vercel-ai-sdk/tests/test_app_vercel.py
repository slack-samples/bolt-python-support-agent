import asyncio
import importlib
import json
import logging
import time
from unittest.mock import AsyncMock, patch
from urllib.parse import quote

import pytest
from slack_bolt.context.async_context import AsyncBoltContext
from slack_bolt.request.async_request import AsyncBoltRequest
from slack_sdk.signature import SignatureVerifier
from vercel.blob import BlobNotFoundError

from listeners.events.message import handle_message

test_logger = logging.getLogger(__name__)


@pytest.fixture(scope="module")
def app_vercel():
    with pytest.MonkeyPatch.context() as monkeypatch:
        monkeypatch.setenv("SLACK_SIGNING_SECRET", "test-secret")
        monkeypatch.setenv("SLACK_CLIENT_ID", "111.222")
        monkeypatch.setenv("SLACK_CLIENT_SECRET", "test-client-secret")
        monkeypatch.setenv("SLACK_BOT_TOKEN", "xoxb-fallback")
        yield importlib.import_module("app_vercel")


async def post_event(
    handler,
    body: str,
    signature: str | None = None,
    content_type: str = "application/json",
) -> dict:
    timestamp = str(int(time.time()))
    if signature is None:
        signature = SignatureVerifier("test-secret").generate_signature(
            timestamp=timestamp, body=body
        )
    scope = {
        "type": "http",
        "method": "POST",
        "path": "/slack/events",
        "query_string": b"",
        "headers": [
            (b"content-type", content_type.encode()),
            (b"x-slack-request-timestamp", timestamp.encode()),
            (b"x-slack-signature", signature.encode()),
        ],
    }
    sent = []

    async def receive():
        return {"type": "http.request", "body": body.encode(), "more_body": False}

    async def send(message):
        sent.append(message)

    await handler(scope, receive, send)
    return {"status": sent[0]["status"], "body": sent[1]["body"]}


class TestAppVercel:
    @pytest.mark.asyncio
    async def test_answers_url_verification(self, app_vercel):
        response = await post_event(
            app_vercel.handler,
            json.dumps({"type": "url_verification", "challenge": "abc"}),
        )

        assert response["status"] == 200
        assert b"abc" in response["body"]

    @pytest.mark.asyncio
    async def test_rejects_bad_signature(self, app_vercel):
        response = await post_event(
            app_vercel.handler,
            json.dumps({"type": "url_verification", "challenge": "abc"}),
            signature="v0=bad",
        )

        assert response["status"] == 401

    @pytest.mark.asyncio
    async def test_falls_back_to_bot_token(self, app_vercel):
        with (
            patch("vercel.blob.get_blob", AsyncMock(side_effect=BlobNotFoundError())),
            patch(
                "slack_sdk.web.async_client.AsyncWebClient.auth_test",
                AsyncMock(
                    return_value={
                        "team_id": "T1",
                        "user_id": "UBOT",
                        "bot_id": "B1",
                    }
                ),
            ),
        ):
            result = await app_vercel.oauth_settings.authorize(
                context=AsyncBoltContext(),
                enterprise_id=None,
                team_id="T1",
                user_id="U1",
            )

        assert result.bot_token == "xoxb-fallback"
        assert result.bot_user_id == "UBOT"

    @pytest.mark.asyncio
    async def test_answers_issue_submission_after_posting_the_issue(self, app_vercel):
        payload = {
            "type": "view_submission",
            "team": {"id": "T1"},
            "user": {"id": "U1", "team_id": "T1"},
            "api_app_id": "A1",
            "view": {
                "id": "V1",
                "type": "modal",
                "callback_id": "issue_submission",
                "team_id": "T1",
                "state": {
                    "values": {
                        "category_block": {
                            "category_select": {
                                "type": "static_select",
                                "selected_option": {"value": "Software Help"},
                            }
                        },
                        "description_block": {
                            "description_input": {
                                "type": "plain_text_input",
                                "value": "Excel crashes on launch",
                            }
                        },
                    }
                },
            },
        }

        with (
            patch("vercel.blob.get_blob", AsyncMock(side_effect=BlobNotFoundError())),
            patch(
                "slack_sdk.web.async_client.AsyncWebClient.auth_test",
                AsyncMock(
                    return_value={
                        "team_id": "T1",
                        "user_id": "UBOT",
                        "bot_id": "B1",
                    }
                ),
            ),
            patch(
                "slack_sdk.web.async_client.AsyncWebClient.conversations_open",
                AsyncMock(return_value={"channel": {"id": "D1"}}),
            ),
            patch(
                "slack_sdk.web.async_client.AsyncWebClient.chat_postMessage",
                AsyncMock(),
            ) as fake_post_message,
        ):
            response = await post_event(
                app_vercel.handler,
                f"payload={quote(json.dumps(payload))}",
                content_type="application/x-www-form-urlencoded",
            )

        assert response["status"] == 200
        fake_post_message.assert_awaited_once_with(
            channel="D1",
            text="*Category:* Software Help\n*Description:* Excel crashes on launch",
            metadata={
                "event_type": "issue_submission",
                "event_payload": {"user_id": "U1"},
            },
        )

    @pytest.mark.asyncio
    async def test_runs_the_agent_for_issue_messages_from_the_bot(self, app_vercel):
        body = {
            "type": "event_callback",
            "team_id": "T1",
            "api_app_id": "A1",
            "event_id": "Ev1",
            "event_time": 1,
            "event": {
                "type": "message",
                "channel": "D1",
                "channel_type": "im",
                "user": "UBOT",
                "bot_id": "B1",
                "text": "*Category:* Software Help",
                "ts": "5.0",
                "metadata": {
                    "event_type": "issue_submission",
                    "event_payload": {"user_id": "U1"},
                },
            },
        }

        with (
            patch("vercel.blob.get_blob", AsyncMock(side_effect=BlobNotFoundError())),
            patch(
                "slack_sdk.web.async_client.AsyncWebClient.auth_test",
                AsyncMock(
                    return_value={
                        "team_id": "T1",
                        "user_id": "UBOT",
                        "bot_id": "B1",
                    }
                ),
            ),
            patch.object(
                app_vercel.app.listener_runner.lazy_listener_runner, "start"
            ) as fake_start,
        ):
            response = await post_event(app_vercel.handler, json.dumps(body))

        assert response["status"] == 200
        fake_start.assert_called_once()
        assert fake_start.call_args.kwargs["function"] == handle_message


class TestWaitUntilLazyListenerRunner:
    @pytest.fixture(autouse=True)
    def setup(self, app_vercel):
        self.runner = app_vercel.WaitUntilLazyListenerRunner(test_logger)
        self.request = AsyncBoltRequest(body="{}", headers={})
        self.finished = asyncio.Event()

    async def lazy_function(self):
        self.finished.set()

    @pytest.mark.asyncio
    async def test_runner_hands_task_to_wait_until(self):
        with patch("app_vercel.wait_until") as fake_wait_until:
            self.runner.start(function=self.lazy_function, request=self.request)

        fake_wait_until.assert_called_once()
        task = fake_wait_until.call_args.args[0]
        assert isinstance(task, asyncio.Task)
        await task
        assert self.finished.is_set()

    @pytest.mark.asyncio
    async def test_runner_runs_without_vercel_context(self):
        self.runner.start(function=self.lazy_function, request=self.request)

        await asyncio.wait_for(self.finished.wait(), timeout=1)
