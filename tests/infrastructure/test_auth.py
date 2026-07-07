from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

import backend.infrastructure.auth.google as google_module
from backend.domain.admin.session import AdminSession
from backend.infrastructure.auth.google import GoogleOAuthAdapter
from backend.infrastructure.auth.session import SessionManager


def test_get_login_url_contains_params():
    adapter = GoogleOAuthAdapter("cid", "secret", "http://cb")
    url = adapter.get_login_url(state="xyz")
    assert url.startswith("https://accounts.google.com/o/oauth2/v2/auth?")
    assert "client_id=cid" in url
    assert "state=xyz" in url
    assert "redirect_uri=http%3A%2F%2Fcb" in url


async def test_exchange_code_returns_email():
    token_resp = MagicMock()
    token_resp.raise_for_status = MagicMock()
    token_resp.json.return_value = {"access_token": "tok"}
    user_resp = MagicMock()
    user_resp.raise_for_status = MagicMock()
    user_resp.json.return_value = {"email": "user@test.local"}

    client = MagicMock()
    client.post = AsyncMock(return_value=token_resp)
    client.get = AsyncMock(return_value=user_resp)
    async_client = MagicMock()
    async_client.__aenter__ = AsyncMock(return_value=client)
    async_client.__aexit__ = AsyncMock(return_value=None)

    adapter = GoogleOAuthAdapter("cid", "secret", "http://cb")
    with patch.object(google_module.httpx, "AsyncClient", return_value=async_client):
        email = await adapter.exchange_code("auth-code")

    assert email == "user@test.local"
    assert client.post.await_args.args[0] == google_module._TOKEN_URL
    assert client.get.await_args.kwargs["headers"] == {"Authorization": "Bearer tok"}


def _session() -> AdminSession:
    return AdminSession(email="admin@test.local", expires_at=datetime.now(timezone.utc))


def test_session_encode_decode_roundtrip():
    manager = SessionManager("secret-key")
    token = manager.encode(_session())
    decoded = manager.decode(token)
    assert decoded.email == "admin@test.local"


def test_session_decode_expired():
    token = SessionManager("secret-key").encode(_session())
    manager = SessionManager("secret-key", max_age=-1)  # already expired
    with pytest.raises(ValueError, match="Session expired"):
        manager.decode(token)


def test_session_decode_invalid_signature():
    token = SessionManager("other-key").encode(_session())
    manager = SessionManager("secret-key")
    with pytest.raises(ValueError, match="Invalid session"):
        manager.decode(token)
