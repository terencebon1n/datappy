"""ProducerService retry/backoff loop — every branch of the ``while True``.

All three ingestors (trip update + alert + vehicle position) share one mock, so
each successful cycle records one ``run`` await per feed type.
"""

from contextlib import contextmanager
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

import backend.application.services.producer as pm
from backend.application.producers.registry import ProducerTask
from backend.domain.gtfs_rt.enums import City, FeedType

_TASK = ProducerTask(city=City.MONTPELLIER, feed_type=FeedType.TRIP_UPDATE, url="u")


@contextmanager
def _wired(run_side_effect, sleep_side_effect):
    kafka = MagicMock()
    kafka.start = AsyncMock()
    kafka.stop = AsyncMock()
    admin = MagicMock()
    admin.ensure_topics = AsyncMock()
    ingestor = MagicMock()
    ingestor.run = AsyncMock(side_effect=run_side_effect)

    with (
        patch.object(pm, "KafkaProducerAdapter", return_value=kafka),
        patch.object(pm, "KafkaAdminTool", return_value=admin),
        patch.object(pm, "TripUpdateGateway", return_value=MagicMock()),
        patch.object(pm, "AlertGateway", return_value=MagicMock()),
        patch.object(pm, "VehiclePositionGateway", return_value=MagicMock()),
        patch.object(pm, "TripIngestorService", return_value=ingestor),
        patch.object(pm, "AlertIngestorService", return_value=ingestor),
        patch.object(pm, "VehiclePositionIngestorService", return_value=ingestor),
        patch.object(pm, "ProducerRegistry") as registry,
        patch.object(pm.asyncio, "sleep", AsyncMock(side_effect=sleep_side_effect)),
    ):
        registry.get_tasks.return_value = [_TASK]
        yield kafka, admin, ingestor


async def test_happy_cycle_then_keyboard_interrupt_breaks():
    # First sleep(10) succeeds (retry_delay reset runs), second breaks the loop.
    with _wired(run_side_effect=None, sleep_side_effect=[None, KeyboardInterrupt]) as (
        kafka,
        admin,
        ingestor,
    ):
        await pm.ProducerService().start(City.MONTPELLIER)

    admin.ensure_topics.assert_awaited_once()
    kafka.start.assert_awaited_once()
    assert ingestor.run.await_count == 6
    kafka.stop.assert_awaited_once()


async def test_every_feed_type_is_ingested_each_cycle():
    with _wired(run_side_effect=None, sleep_side_effect=[KeyboardInterrupt]) as (
        _kafka,
        _admin,
        _ingestor,
    ):
        with patch.object(pm.ProducerRegistry, "get_tasks") as get_tasks:
            get_tasks.return_value = [_TASK]
            await pm.ProducerService().start(City.MONTPELLIER)

    assert {call.kwargs["feed"] for call in get_tasks.call_args_list} == {
        FeedType.TRIP_UPDATE,
        FeedType.ALERT,
        FeedType.VEHICLE_POSITION,
    }


async def test_generic_exception_triggers_backoff_then_recovers():
    # iter1: trip run raises -> except -> sleep(30) ok -> retry_delay doubled.
    # iter2: all three runs ok -> sleep(10) raises KeyboardInterrupt -> break.
    with _wired(
        run_side_effect=[RuntimeError("boom"), None, None, None],
        sleep_side_effect=[None, KeyboardInterrupt],
    ) as (kafka, admin, ingestor):
        await pm.ProducerService().start(City.MONTPELLIER)

    assert ingestor.run.await_count == 4
    kafka.stop.assert_awaited_once()


async def test_gives_up_when_max_retry_delay_reached(monkeypatch):
    # With max == initial, the very first failure hits the ``>= MAX`` branch.
    monkeypatch.setattr(pm, "_MAX_RETRY_DELAY", pm._INITIAL_RETRY_DELAY)
    with _wired(run_side_effect=RuntimeError("fatal"), sleep_side_effect=[None]) as (
        kafka,
        _admin,
        _ingestor,
    ):
        with pytest.raises(RuntimeError, match="fatal"):
            await pm.ProducerService().start(City.MONTPELLIER)

    # loop aborted before a clean stop
    kafka.stop.assert_not_awaited()
