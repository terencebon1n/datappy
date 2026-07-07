"""ProducerService retry/backoff loop — every branch of the ``while True``."""

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
        patch.object(pm, "TripIngestorService", return_value=ingestor),
        patch.object(pm, "ProducerRegistry") as registry,
        patch.object(pm.asyncio, "sleep", AsyncMock(side_effect=sleep_side_effect)),
    ):
        registry.get_tasks.return_value = [_TASK]
        yield kafka, admin, ingestor


async def test_happy_cycle_then_keyboard_interrupt_breaks():
    # First sleep(10) succeeds (retry_delay reset runs), second breaks the loop.
    with _wired(
        run_side_effect=None, sleep_side_effect=[None, KeyboardInterrupt]
    ) as (kafka, admin, ingestor):
        await pm.ProducerService().start(City.MONTPELLIER)

    admin.ensure_topics.assert_awaited_once()
    kafka.start.assert_awaited_once()
    assert ingestor.run.await_count == 2
    kafka.stop.assert_awaited_once()


async def test_generic_exception_triggers_backoff_then_recovers():
    # iter1: run raises -> except -> sleep(30) ok -> retry_delay doubled.
    # iter2: run ok -> sleep(10) raises KeyboardInterrupt -> break.
    with _wired(
        run_side_effect=[RuntimeError("boom"), None],
        sleep_side_effect=[None, KeyboardInterrupt],
    ) as (kafka, admin, ingestor):
        await pm.ProducerService().start(City.MONTPELLIER)

    assert ingestor.run.await_count == 2
    kafka.stop.assert_awaited_once()


async def test_gives_up_when_max_retry_delay_reached(monkeypatch):
    # With max == initial, the very first failure hits the ``>= MAX`` branch.
    monkeypatch.setattr(pm, "_MAX_RETRY_DELAY", pm._INITIAL_RETRY_DELAY)
    with _wired(
        run_side_effect=RuntimeError("fatal"), sleep_side_effect=[None]
    ) as (kafka, _admin, _ingestor):
        with pytest.raises(RuntimeError, match="fatal"):
            await pm.ProducerService().start(City.MONTPELLIER)

    # loop aborted before a clean stop
    kafka.stop.assert_not_awaited()
