from unittest.mock import MagicMock

import pytest

from backend.application.services.admin.auth import AdminAuthService
from backend.application.services.admin.process_manager import ProcessManagerService
from backend.domain.admin.process import (
    ManagedProcess,
    ManagedServiceType,
    ProcessStatus,
)
from backend.domain.gtfs_rt.enums import City


def test_authorize_allowed_email_returns_session():
    service = AdminAuthService(allowed_email="admin@test.local")
    session = service.authorize("admin@test.local")
    assert session.email == "admin@test.local"
    assert session.expires_at is not None


def test_authorize_wrong_email_raises():
    service = AdminAuthService(allowed_email="admin@test.local")
    with pytest.raises(PermissionError, match="not authorized"):
        service.authorize("intruder@evil.local")


def test_process_manager_delegates_to_adapter():
    adapter = MagicMock()
    managed = ManagedProcess(
        service=ManagedServiceType.PRODUCER,
        city=City.MONTPELLIER,
        status=ProcessStatus.RUNNING,
        container_name="c",
    )
    adapter.run_service.return_value = managed
    adapter.get_all_status.return_value = [managed]

    service = ProcessManagerService(adapter)

    assert service.start(ManagedServiceType.PRODUCER, City.MONTPELLIER) is managed
    adapter.run_service.assert_called_once_with(
        ManagedServiceType.PRODUCER, City.MONTPELLIER
    )

    service.stop(ManagedServiceType.CONSUMER, City.NIMES)
    adapter.stop_service.assert_called_once_with(
        ManagedServiceType.CONSUMER, City.NIMES
    )

    assert service.get_all_status() == [managed]
    service.close()
    adapter.close.assert_called_once()
