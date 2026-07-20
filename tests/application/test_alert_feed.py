"""AlertFeedService — keeps only alerts active now and linked to the selection."""

from unittest.mock import AsyncMock

import backend.application.services.api.alert_feed as feed_module
from backend.application.dto.alert import AlertPathDTO
from backend.application.services.api.alert_feed import AlertFeedService
from backend.domain.gtfs_rt.alert import Alert, InformedEntity, Period
from backend.domain.gtfs_rt.enums import AlertSeverity, City

_PATH = AlertPathDTO(city=City.MONTPELLIER, route_id="R1", direction_id=0, stop_id="S1")


def _repository(alerts: list[Alert]) -> AsyncMock:
    repository = AsyncMock()
    repository.get_alerts.return_value = alerts
    return repository


async def test_returns_only_linked_alerts():
    linked = Alert(id="linked", informed_entities=[InformedEntity(route_id="R1")])
    unlinked = Alert(id="unlinked", informed_entities=[InformedEntity(route_id="R2")])
    repository = _repository([linked, unlinked])

    result = await AlertFeedService(repository).get_alerts(_PATH)

    assert [alert.id for alert in result] == ["linked"]
    repository.get_alerts.assert_awaited_once_with(City.MONTPELLIER)


async def test_drops_expired_alerts(monkeypatch):
    monkeypatch.setattr(feed_module, "datetime", _frozen_clock(1_000))
    expired = Alert(
        id="expired",
        active_periods=[Period(start=1, end=2)],
        informed_entities=[InformedEntity(route_id="R1")],
    )
    current = Alert(
        id="current",
        active_periods=[Period(start=900, end=1_100)],
        informed_entities=[InformedEntity(route_id="R1")],
    )

    result = await AlertFeedService(_repository([expired, current])).get_alerts(_PATH)

    assert [alert.id for alert in result] == ["current"]


async def test_sorts_by_severity_then_id():
    alerts = [
        Alert(
            id="b",
            severity=AlertSeverity.INFO,
            informed_entities=[InformedEntity(route_id="R1")],
        ),
        Alert(
            id="a",
            severity=AlertSeverity.INFO,
            informed_entities=[InformedEntity(route_id="R1")],
        ),
        Alert(
            id="c",
            severity=AlertSeverity.SEVERE,
            informed_entities=[InformedEntity(route_id="R1")],
        ),
    ]

    result = await AlertFeedService(_repository(alerts)).get_alerts(_PATH)

    assert [alert.id for alert in result] == ["c", "a", "b"]


async def test_route_only_selection_matches_every_stop():
    path = AlertPathDTO(city=City.MONTPELLIER, route_id="R1")
    alert = Alert(id="a", informed_entities=[InformedEntity(route_id="R1")])

    result = await AlertFeedService(_repository([alert])).get_alerts(path)

    assert [alert.id for alert in result] == ["a"]


def _frozen_clock(epoch: int):  # noqa: ANN202
    from datetime import datetime as real_datetime
    from datetime import timezone

    class _Frozen(real_datetime):
        @classmethod
        def now(cls, tz=None):  # noqa: ANN001, ANN206
            return real_datetime.fromtimestamp(epoch, tz=tz or timezone.utc)

    return _Frozen
