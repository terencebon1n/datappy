import pytest

from backend.application.services.enums import ServiceCommand
from backend.application.services.registry import ServiceRegistry


class _AsyncService:
    def __init__(self) -> None:
        self.called_with = "unset"

    async def start(self, city=None) -> None:
        self.called_with = city


class _SyncService:
    def __init__(self) -> None:
        self.called_with = "unset"

    def start(self, city=None) -> None:
        self.called_with = city


def test_run_unknown_service_raises():
    registry = ServiceRegistry()
    with pytest.raises(ValueError, match="Unknown service: nope"):
        registry.run("nope")


def test_run_async_service_with_and_without_city():
    registry = ServiceRegistry()

    with_city = _AsyncService()
    without_city = _AsyncService()
    registry.register(ServiceCommand.PRODUCER, lambda: with_city)
    registry.register(ServiceCommand.CONSUMER, lambda: without_city)

    registry.run(ServiceCommand.PRODUCER, "montpellier")
    assert str(with_city.called_with) == "montpellier"

    registry.run(ServiceCommand.CONSUMER)
    assert without_city.called_with is None


def test_run_sync_service_with_and_without_city():
    registry = ServiceRegistry()

    with_city = _SyncService()
    without_city = _SyncService()
    registry.register(ServiceCommand.POPULATE, lambda: with_city)
    registry.register(ServiceCommand.DIAGRAM, lambda: without_city)

    registry.run(ServiceCommand.POPULATE, "nimes")
    assert str(with_city.called_with) == "nimes"

    registry.run(ServiceCommand.DIAGRAM)
    assert without_city.called_with is None
