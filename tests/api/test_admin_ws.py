from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

import pytest
from fastapi import WebSocketDisconnect

import backend.api.v1.endpoints.admin as admin_module
from backend.domain.admin.process import (
    ManagedProcess,
    ManagedServiceType,
    ProcessStatus,
)
from backend.domain.admin.session import AdminSession
from backend.domain.gtfs_rt.enums import City


def _session() -> AdminSession:
    return AdminSession(email="admin@test.local", expires_at=datetime.now(timezone.utc))


def _managed() -> ManagedProcess:
    return ManagedProcess(
        service=ManagedServiceType.PRODUCER,
        city=City.MONTPELLIER,
        status=ProcessStatus.RUNNING,
        container_name="c",
    )


def test_ws_status_streams_updates(client, monkeypatch):
    # Fast poll so the produce loop iterates (skip + timeout branches).
    monkeypatch.setattr(
        admin_module.settings.admin, "status_poll_interval_seconds", 0.01
    )

    running = _managed()
    stopped = ManagedProcess(
        service=ManagedServiceType.PRODUCER,
        city=City.MONTPELLIER,
        status=ProcessStatus.STOPPED,
        container_name="c",
    )
    # Poll 1 = running (send), poll 2 = running again (unchanged -> skip branch),
    # poll 3+ = stopped (send). The client blocks on the second message, so the
    # skip iteration is guaranteed to run before the test proceeds.
    snapshots = iter([[running], [running]])

    def status_snapshot():  # noqa: ANN202
        try:
            return next(snapshots)
        except StopIteration:
            return [stopped]

    with (
        patch.object(admin_module, "session_manager") as session_manager,
        patch.object(admin_module, "process_manager") as process_manager,
    ):
        session_manager.decode.return_value = _session()
        process_manager.get_all_status.side_effect = status_snapshot

        client.cookies.set("admin_session", "tok")
        with client.websocket_connect("/admin/status") as ws:
            first = ws.receive_json()
            ws.send_text("refresh")  # exercises the refresh (non-timeout) path
            second = ws.receive_json()
            assert first[0]["status"] == "running"
            assert second[0]["status"] == "stopped"
    client.cookies.clear()


def test_ws_status_rejects_without_session(client):
    client.cookies.clear()
    with pytest.raises(WebSocketDisconnect):
        with client.websocket_connect("/admin/status"):
            pass


def test_ws_status_rejects_invalid_token(client):
    with patch.object(admin_module, "session_manager") as session_manager:
        session_manager.decode.side_effect = ValueError("bad token")
        client.cookies.set("admin_session", "bad")
        with pytest.raises(WebSocketDisconnect):
            with client.websocket_connect("/admin/status"):
                pass
    client.cookies.clear()
