from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

from backend.application.dto.departure import StopDeparturePathDTO
from backend.application.services.api.stop_departure_feed import StopDepartureFeed
from backend.domain.gtfs_rt.enums import City
from backend.domain.gtfs_rt.stop_update import StopUpdate

_NOW = int(datetime.now(tz=timezone.utc).timestamp())


def _selection(limit: int = 6) -> StopDeparturePathDTO:
    return StopDeparturePathDTO(
        city=City.MONTPELLIER, route_id="r1", stop_id="s1", limit=limit
    )


def _stop_update(trip_id: str, in_seconds: int) -> StopUpdate:
    return StopUpdate(
        trip_id=trip_id,
        timestamp=_NOW,
        departure_time=_NOW + in_seconds,
        departure_delay=30,
        arrival_time=_NOW + in_seconds,
        arrival_delay=0,
    )


def _scheduled_row(trip_id: str, clock: str, direction_id: int, headsign: str):
    return SimpleNamespace(
        trip_id=trip_id,
        departure_time=clock,
        direction_id=direction_id,
        headsign=headsign,
    )


def _feed(realtime_by_direction=None, scheduled_rows=(), headsign_rows=()):
    realtime_by_direction = realtime_by_direction or {}
    stop_updates = MagicMock()
    stop_updates.get_stop_updates = AsyncMock(
        side_effect=lambda city, route_id, direction_id, stop_id: list(
            realtime_by_direction.get(direction_id, [])
        )
    )
    stop_times = MagicMock()
    stop_times.get_stop_departures = AsyncMock(return_value=list(scheduled_rows))
    trips = MagicMock()
    trips.get_trip_headsigns = AsyncMock(return_value=list(headsign_rows))
    feed = StopDepartureFeed(stop_updates, stop_times, trips)
    return feed, stop_updates, stop_times, trips


async def test_reads_realtime_for_both_directions():
    feed, stop_updates, _, _ = _feed()

    await feed.get_departures(_selection())

    directions = {
        call.kwargs["direction_id"]
        for call in stop_updates.get_stop_updates.await_args_list
    }
    assert directions == {0, 1}


async def test_realtime_departures_carry_their_direction_and_headsign():
    feed, _, _, trips = _feed(
        realtime_by_direction={0: [_stop_update("t1", 120)]},
        headsign_rows=[SimpleNamespace(id="t1", direction_id=0, headsign="Mosson")],
    )

    departures = await feed.get_departures(_selection())

    assert departures[0].trip_id == "t1"
    assert departures[0].direction_id == 0
    assert departures[0].headsign == "Mosson"
    assert departures[0].departure_delay == 30
    assert departures[0].is_realtime is True
    trips.get_trip_headsigns.assert_awaited_once_with(["t1"])


async def test_headsign_falls_back_to_empty_when_the_trip_is_unknown():
    feed, _, _, _ = _feed(realtime_by_direction={0: [_stop_update("t1", 120)]})

    departures = await feed.get_departures(_selection())

    assert departures[0].headsign == ""


async def test_no_headsign_lookup_without_realtime_departures():
    feed, _, _, trips = _feed()

    await feed.get_departures(_selection())

    trips.get_trip_headsigns.assert_not_awaited()


async def test_stale_realtime_departures_are_dropped():
    stale = StopUpdate(
        trip_id="old",
        timestamp=_NOW - 3600,
        departure_time=_NOW - 3600,
        departure_delay=0,
        arrival_time=_NOW - 3600,
        arrival_delay=0,
    )
    feed, _, _, _ = _feed(realtime_by_direction={0: [stale]})

    assert await feed.get_departures(_selection()) == []


async def test_scheduled_departures_fill_in_and_are_not_realtime():
    feed, _, _, _ = _feed(
        scheduled_rows=[_scheduled_row("t2", "23:59:00", 1, "Odysseum")]
    )

    departures = await feed.get_departures(_selection())

    assert departures[0].trip_id == "t2"
    assert departures[0].direction_id == 1
    assert departures[0].headsign == "Odysseum"
    assert departures[0].is_realtime is False
    assert departures[0].departure_delay == 0


async def test_a_trip_seen_live_is_not_repeated_from_the_schedule():
    feed, _, _, _ = _feed(
        realtime_by_direction={0: [_stop_update("t1", 120)]},
        scheduled_rows=[_scheduled_row("t1", "23:59:00", 0, "Mosson")],
        headsign_rows=[SimpleNamespace(id="t1", direction_id=0, headsign="Mosson")],
    )

    departures = await feed.get_departures(_selection())

    assert [departure.trip_id for departure in departures] == ["t1"]
    assert departures[0].is_realtime is True


async def test_departures_are_sorted_by_time_across_directions():
    feed, _, _, _ = _feed(
        realtime_by_direction={
            0: [_stop_update("late", 600)],
            1: [_stop_update("soon", 60)],
        },
        headsign_rows=[
            SimpleNamespace(id="late", direction_id=0, headsign="Mosson"),
            SimpleNamespace(id="soon", direction_id=1, headsign="Odysseum"),
        ],
    )

    departures = await feed.get_departures(_selection())

    assert [departure.trip_id for departure in departures] == ["soon", "late"]


async def test_limit_caps_the_feed():
    feed, _, _, _ = _feed(
        realtime_by_direction={
            0: [_stop_update("a", 60), _stop_update("b", 120)],
            1: [_stop_update("c", 180)],
        },
        headsign_rows=[
            SimpleNamespace(id=t, direction_id=0, headsign="H") for t in "abc"
        ],
    )

    departures = await feed.get_departures(_selection(limit=2))

    assert [departure.trip_id for departure in departures] == ["a", "b"]


async def test_the_schedule_query_uses_the_requested_limit():
    feed, _, stop_times, _ = _feed()

    await feed.get_departures(_selection(limit=4))

    assert stop_times.get_stop_departures.await_args.kwargs["limit"] == 4
    assert stop_times.get_stop_departures.await_args.kwargs["route_id"] == "r1"
    assert stop_times.get_stop_departures.await_args.kwargs["stop_id"] == "s1"


async def test_an_empty_stop_yields_no_departures():
    feed, _, _, _ = _feed()

    assert await feed.get_departures(_selection()) == []
