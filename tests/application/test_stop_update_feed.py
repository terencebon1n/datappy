from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock

from backend.application.dto.stop import TransitPathDTO
from backend.application.services.api.stop_update_feed import (
    StopUpdateFeed,
    _clock_to_epoch,
)
from backend.domain.gtfs.scheduled_departure import ScheduledDeparture
from backend.domain.gtfs_rt.enums import City
from backend.domain.gtfs_rt.stop_update import StopUpdate


def _transit() -> TransitPathDTO:
    return TransitPathDTO(
        city=City.MONTPELLIER,
        route_id="r1",
        direction_id=0,
        stop_id__origin="origin",
        stop_id__destination="dest",
    )


def test_clock_to_epoch():
    assert _clock_to_epoch("00:00:00", 1000) == 1000
    assert _clock_to_epoch("01:02:03", 0) == 3600 + 120 + 3


async def test_get_updates_merges_realtime_and_estimated():
    now_ts = int(datetime.now(tz=timezone.utc).timestamp())

    active_reachable = StopUpdate(
        trip_id="active_ok",
        timestamp=now_ts,
        departure_time=now_ts + 1800,
        departure_delay=0,
        arrival_time=now_ts + 1800,
        arrival_delay=0,
    )
    active_unreachable = StopUpdate(
        trip_id="active_no",
        timestamp=now_ts,
        departure_time=now_ts + 1800,
        departure_delay=0,
        arrival_time=now_ts + 1800,
        arrival_delay=0,
    )
    stale = StopUpdate(
        trip_id="stale",
        timestamp=now_ts - 3600,
        departure_time=now_ts + 1800,
        departure_delay=0,
        arrival_time=now_ts + 1800,
        arrival_delay=0,
    )

    stop_update_repo = MagicMock()
    stop_update_repo.get_stop_updates = AsyncMock(
        return_value=[active_reachable, active_unreachable, stale]
    )

    schedule_repo = MagicMock()
    # Only "active_ok" is reachable to the destination.
    schedule_repo.get_reachable_trip_ids = AsyncMock(return_value=["active_ok"])
    schedule_repo.get_scheduled_departures = AsyncMock(
        return_value=[
            # duplicate of a realtime trip -> filtered out
            ScheduledDeparture(
                trip_id="active_ok",
                departure_time="23:00:00",
                arrival_time="23:00:00",
            ),
            ScheduledDeparture(
                trip_id="sched1", departure_time="08:00:00", arrival_time="08:00:00"
            ),
            ScheduledDeparture(
                trip_id="sched2", departure_time="09:00:00", arrival_time="09:00:00"
            ),
        ]
    )

    feed = StopUpdateFeed(stop_update_repo, schedule_repo)
    result = await feed.get_updates(_transit())

    trip_ids = [su.trip_id for su in result]
    assert "active_ok" in trip_ids  # active + reachable
    assert "active_no" not in trip_ids  # active but unreachable
    assert "stale" not in trip_ids  # stale -> dropped
    assert "sched1" in trip_ids and "sched2" in trip_ids  # estimated
    assert trip_ids.count("active_ok") == 1  # scheduled dup removed
    # estimated departures are non-realtime
    assert any(su.is_realtime is False for su in result)
    # sorted ascending by departure_time
    assert trip_ids == [
        su.trip_id for su in sorted(result, key=lambda s: s.departure_time)
    ]

    schedule_repo.get_reachable_trip_ids.assert_awaited_once()
    stop_update_repo.get_stop_updates.assert_awaited_once()


async def test_get_updates_truncates_to_feed_size():
    now_ts = int(datetime.now(tz=timezone.utc).timestamp())
    stop_update_repo = MagicMock()
    stop_update_repo.get_stop_updates = AsyncMock(return_value=[])
    schedule_repo = MagicMock()
    schedule_repo.get_reachable_trip_ids = AsyncMock(return_value=[])
    schedule_repo.get_scheduled_departures = AsyncMock(
        return_value=[
            ScheduledDeparture(
                trip_id=f"t{i}",
                departure_time=f"{8 + i:02d}:00:00",
                arrival_time=f"{8 + i:02d}:00:00",
            )
            for i in range(8)
        ]
    )

    feed = StopUpdateFeed(stop_update_repo, schedule_repo)
    result = await feed.get_updates(_transit())

    assert len(result) == 5  # _FEED_SIZE
    assert now_ts  # sanity: reference timestamp computed
