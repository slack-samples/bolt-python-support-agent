"""HMAC-signed OAuth state token helpers."""

import base64
import hashlib
import hmac
import json
import os
import secrets


def _signing_key() -> bytes:
    return os.environ["SLACK_APP_CLIENT_SECRET"].encode()


def generate_state(team_id: str | None, enterprise_id: str | None) -> str:
    """Create an HMAC-SHA256 signed state token encoding team/enterprise IDs."""
    payload = json.dumps(
        {
            "team_id": team_id,
            "enterprise_id": enterprise_id,
            "nonce": secrets.token_hex(16),
        },
        separators=(",", ":"),
    )
    payload_b64 = base64.urlsafe_b64encode(payload.encode()).decode()
    sig = hmac.new(_signing_key(), payload_b64.encode(), hashlib.sha256).hexdigest()
    return f"{payload_b64}.{sig}"


def verify_state(state: str) -> dict | None:
    """Verify an HMAC-signed state token. Returns the payload dict or None."""
    parts = state.split(".", 1)
    if len(parts) != 2:
        return None
    payload_b64, sig = parts
    expected_sig = hmac.new(
        _signing_key(), payload_b64.encode(), hashlib.sha256
    ).hexdigest()
    if not hmac.compare_digest(sig, expected_sig):
        return None
    try:
        return json.loads(base64.urlsafe_b64decode(payload_b64))
    except Exception:
        return None
