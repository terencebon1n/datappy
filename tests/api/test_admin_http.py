from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import backend.api.v1.endpoints.admin as admin_module
from backend.api.dependencies import require_admin_session
from backend.domain.admin.process import (
    ManagedProcess,
    ManagedServiceType,
    ProcessStatus,
)
from backend.domain.admin.session import AdminSession
from backend.domain.gtfs_rt.enums import City


def _session() -> AdminSession:
    return AdminSession(email="admin@test.local", expires_at=datetime.now(timezone.utc))


def test_login_redirects_to_google(client):
    with patch.object(
        admin_module.google_oauth, "get_login_url", return_value="http://login-url"
    ):
        response = client.get("/admin/login", follow_redirects=False)
    assert response.status_code == 307
    assert response.headers["location"] == "http://login-url"


def test_callback_success_sets_cookie(client):
    with (
        patch.object(
            admin_module.google_oauth,
            "exchange_code",
            new=AsyncMock(return_value="admin@test.local"),
        ),
        patch.object(admin_module.auth_service, "authorize", return_value=_session()),
        patch.object(admin_module.session_manager, "encode", return_value="token"),
    ):
        response = client.get(
            "/admin/callback", params={"code": "xyz"}, follow_redirects=False
        )
    assert response.status_code == 307
    assert "admin_session=token" in response.headers.get("set-cookie", "")


def test_callback_exchange_failure_returns_400(client):
    with patch.object(
        admin_module.google_oauth,
        "exchange_code",
        new=AsyncMock(side_effect=RuntimeError("bad code")),
    ):
        response = client.get(
            "/admin/callback", params={"code": "xyz"}, follow_redirects=False
        )
    assert response.status_code == 400


def test_callback_unauthorized_email_returns_403(client):
    with (
        patch.object(
            admin_module.google_oauth,
            "exchange_code",
            new=AsyncMock(return_value="intruder@evil.local"),
        ),
        patch.object(
            admin_module.auth_service,
            "authorize",
            side_effect=PermissionError("nope"),
        ),
    ):
        response = client.get(
            "/admin/callback", params={"code": "xyz"}, follow_redirects=False
        )
    assert response.status_code == 403


def test_logout_clears_cookie(client):
    response = client.get("/admin/logout")
    assert response.status_code == 204
    assert "admin_session=" in response.headers.get("set-cookie", "")


def test_start_service_success(app, client):
    app.dependency_overrides[require_admin_session] = _session
    managed = ManagedProcess(
        service=ManagedServiceType.PRODUCER,
        city=City.MONTPELLIER,
        status=ProcessStatus.RUNNING,
        container_name="c",
    )
    with patch.object(admin_module.process_manager, "start", return_value=managed):
        response = client.post("/admin/producer/montpellier/start")
    assert response.status_code == 200
    assert response.json()["status"] == "running"


def test_start_service_failure_returns_500(app, client):
    app.dependency_overrides[require_admin_session] = _session
    with patch.object(
        admin_module.process_manager, "start", side_effect=RuntimeError("boom")
    ):
        response = client.post("/admin/producer/montpellier/start")
    assert response.status_code == 500


def test_stop_service_success(app, client):
    app.dependency_overrides[require_admin_session] = _session
    with patch.object(admin_module.process_manager, "stop", return_value=None) as stop:
        response = client.post("/admin/consumer/nimes/stop")
    assert response.status_code == 200
    stop.assert_called_once()


def test_stop_service_missing_container_returns_404(app, client):
    app.dependency_overrides[require_admin_session] = _session
    with patch.object(
        admin_module.process_manager, "stop", side_effect=ValueError("not found")
    ):
        response = client.post("/admin/producer/montpellier/stop")
    assert response.status_code == 404
