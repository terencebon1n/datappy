import asyncio as _asyncio
import time as _time
from unittest.mock import AsyncMock, MagicMock, patch

import backend.api.v1.endpoints.transit as transit
from backend.domain.gtfs_rt.stop_update import StopUpdate

from .conftest import FakeAsyncCM

_ORIGINAL_SLEEP = _asyncio.sleep
_ORIGINAL_TIME_SLEEP = _time.sleep

_WS_URL = (
    "/stop-updates?city=montpellier&route_id=r1&direction_id=0"
    "&stop_id__origin=a&stop_id__destination=b"
)


async def _yield_sleep(*_args, **_kwargs) -> None:
    # Yield to the loop (so the disconnect is processed) without a real delay.
    await _ORIGINAL_SLEEP(0)


def _stop_update() -> StopUpdate:
    return StopUpdate(
        trip_id="t1",
        timestamp=1,
        departure_time=2,
        departure_delay=0,
        arrival_time=2,
        arrival_delay=0,
    )


def test_ws_stop_updates_streams_then_disconnects(client):
    with (
        patch.object(transit, "gtfs_engine_for", return_value=MagicMock()),
        patch.object(transit, "AsyncSession", FakeAsyncCM),
        patch.object(transit, "StopUpdateFeed") as feed_cls,
        patch.object(transit.asyncio, "sleep", new=_yield_sleep),
    ):
        feed_cls.return_value.get_updates = AsyncMock(return_value=[_stop_update()])
        with client.websocket_connect(_WS_URL) as ws:
            message = ws.receive_json()
            assert message[0]["trip_id"] == "t1"


def test_ws_stop_updates_closes_on_feed_error(client):
    with (
        patch.object(transit, "gtfs_engine_for", return_value=MagicMock()),
        patch.object(transit, "AsyncSession", FakeAsyncCM),
        patch.object(transit, "StopUpdateFeed") as feed_cls,
        patch.object(transit.asyncio, "sleep", new=_yield_sleep),
    ):
        feed_cls.return_value.get_updates = AsyncMock(
            side_effect=RuntimeError("db down")
        )
        with client.websocket_connect(_WS_URL):
            _ORIGINAL_TIME_SLEEP(0.2)  # let produce hit the error branch
        feed_cls.return_value.get_updates.assert_awaited()
