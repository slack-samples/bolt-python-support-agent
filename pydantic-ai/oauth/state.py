"""HMAC-signed OAuth state token helpers."""

import base64
import hashlib
import hmac
import json
import secrets

from constants import SLACK_APP_CLIENT_SECRET


def _signing_key() -> bytes:
    return SLACK_APP_CLIENT_SECRET.encode()


def generate_state() -> str:
    """Create an HMAC-SHA256 signed CSRF state token."""
    payload = json.dumps(
        {"nonce": secrets.token_hex(16)},
        separators=(",", ":"),
    )
    payload_b64 = base64.urlsafe_b64encode(payload.encode()).decode()
    sig = hmac.new(_signing_key(), payload_b64.encode(), hashlib.sha256).hexdigest()
    return f"{payload_b64}.{sig}"


def consume_state(state: str) -> bool:
    """Verify an HMAC-signed state token. Returns True if the signature is valid."""
    parts = state.split(".", 1)
    if len(parts) != 2:
        return False
    payload_b64, sig = parts
    expected_sig = hmac.new(
        _signing_key(), payload_b64.encode(), hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(sig, expected_sig)
