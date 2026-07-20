from unittest.mock import MagicMock, patch

import pytest
from docker.errors import NotFound

import backend.infrastructure.docker.adapter as adapter_module
from backend.domain.admin.process import ManagedServiceType, ProcessStatus
from backend.domain.gtfs_rt.enums import City
from backend.infrastructure.docker.adapter import (
    DockerContainerStatus,
    DockerProcessAdapter,
    DockerRestartPolicy,
)


def test_container_status_to_process_status():
    assert DockerContainerStatus.RUNNING.to_process_status() == ProcessStatus.RUNNING
    assert DockerContainerStatus.RESTARTING.to_process_status() == ProcessStatus.RUNNING
    assert DockerContainerStatus.EXITED.to_process_status() == ProcessStatus.CRASHED
    assert DockerContainerStatus.CREATED.to_process_status() == ProcessStatus.STOPPED
    assert DockerContainerStatus.PAUSED.to_process_status() == ProcessStatus.STOPPED


def test_restart_policy_config():
    assert DockerRestartPolicy.ON_FAILURE.config(max_retries=5) == {
        "Name": "on-failure",
        "MaximumRetryCount": 5,
    }
    assert DockerRestartPolicy.ALWAYS.config() == {
        "Name": "always",
        "MaximumRetryCount": 0,
    }


def _adapter_with_client(client: MagicMock) -> DockerProcessAdapter:
    with patch.object(adapter_module.docker, "DockerClient", return_value=client):
        adapter = DockerProcessAdapter(image="img", network="net", host="unix://sock")
        # trigger lazy client creation while the patch is active
        _ = adapter._client
    return adapter


def test_run_service_removes_existing_then_runs():
    client = MagicMock()
    adapter = _adapter_with_client(client)

    proc = adapter.run_service(ManagedServiceType.PRODUCER, City.MONTPELLIER)

    client.containers.get.assert_called_once_with("datappy_producer_montpellier")
    client.containers.get.return_value.remove.assert_called_once_with(force=True)
    client.containers.run.assert_called_once()
    assert proc.status == ProcessStatus.RUNNING
    assert proc.container_name == "datappy_producer_montpellier"


def test_run_service_uses_the_installed_console_script():
    # The image exposes `backend.main:main` as the `datappy` script (same entry
    # point as the Dockerfile CMD); there is no importable top-level `main`.
    client = MagicMock()
    adapter = _adapter_with_client(client)

    adapter.run_service(ManagedServiceType.CONSUMER, City.MONTPELLIER)

    assert client.containers.run.call_args.kwargs["command"] == [
        "datappy",
        "consumer",
        "montpellier",
    ]


def test_run_service_when_container_absent():
    client = MagicMock()
    client.containers.get.side_effect = NotFound("absent")
    adapter = _adapter_with_client(client)

    proc = adapter.run_service(ManagedServiceType.CONSUMER, City.NIMES)

    client.containers.run.assert_called_once()
    assert proc.container_name == "datappy_consumer_nimes"


def test_stop_service_stops_and_removes():
    client = MagicMock()
    container = client.containers.get.return_value
    adapter = _adapter_with_client(client)

    adapter.stop_service(ManagedServiceType.PRODUCER, City.TOULOUSE)

    container.stop.assert_called_once()
    container.remove.assert_called_once()


def test_stop_service_absent_raises():
    client = MagicMock()
    client.containers.get.side_effect = NotFound("absent")
    adapter = _adapter_with_client(client)

    with pytest.raises(ValueError, match="No container found"):
        adapter.stop_service(ManagedServiceType.PRODUCER, City.TOULOUSE)


def test_close_disposes_client_once():
    client = MagicMock()
    adapter = _adapter_with_client(client)
    adapter.close()
    client.close.assert_called_once()


def test_close_without_client_is_noop():
    adapter = DockerProcessAdapter(image="img", network="net", host="unix://sock")
    adapter.close()  # __client is None -> nothing happens


def test_get_all_status_running():
    client = MagicMock()
    client.containers.get.return_value = MagicMock(status="running")
    adapter = _adapter_with_client(client)

    statuses = adapter.get_all_status()

    assert len(statuses) == len(ManagedServiceType) * len(City)
    assert all(s.status == ProcessStatus.RUNNING for s in statuses)


def test_get_all_status_handles_missing_and_invalid():
    client = MagicMock()
    invalid = MagicMock(status="dead")  # not a DockerContainerStatus -> ValueError
    client.containers.get.side_effect = [NotFound("x")] + [invalid] * 7
    adapter = _adapter_with_client(client)

    statuses = adapter.get_all_status()

    assert all(s.status == ProcessStatus.STOPPED for s in statuses)
