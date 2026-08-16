from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

from backend.application.dto.departure import StopDeparturePathDTO
from backend.application.services.api.stop_departure_feed import StopDepartureFeed
from backend.domain.gtfs_rt.enums import City
from backend.domain.gtfs_rt.stop_update import StopUpdate

_NOW = int(datetime.now(tz=timezone.utc).timestamp())


def _selection(limit: int = 4) -> StopDeparturePathDTO:
    return StopDeparturePathDTO(city=City.MONTPELLIER, stop_id="s1", limit=limit)


def _stop_update(trip_id: str, in_seconds: int) -> StopUpdate:
    return StopUpdate(
        trip_id=trip_id,
        timestamp=_NOW,
        departure_time=_NOW + in_seconds,
        departure_delay=30,
        arrival_time=_NOW + in_seconds,
        arrival_delay=0,
    )


def _scheduled_row(
    trip_id: str,
    clock: str,
    direction_id: int = 0,
    headsign: str = "Mosson",
    route_id: str = "r1",
    short_name: str = "1",
):
    return SimpleNamespace(
        trip_id=trip_id,
        departure_time=clock,
        direction_id=direction_id,
        headsign=headsign,
        route_id=route_id,
        route_short_name=short_name,
        route_color="005CA9",
        route_type=0,
    )


def _service_key(route_id: str = "r1", direction_id: int = 0, stop_id: str = "s1"):
    return SimpleNamespace(
        route_id=route_id, direction_id=direction_id, stop_id=stop_id
    )


def _feed(
    realtime_by_key=None,
    scheduled_rows=(),
    headsign_rows=(),
    sibling_ids=("s1",),
    service_keys=(),
):
    realtime_by_key = realtime_by_key or {}
    stop_updates = MagicMock()
    stop_updates.get_stop_updates = AsyncMock(
        side_effect=lambda city, route_id, direction_id, stop_id: list(
            realtime_by_key.get((route_id, direction_id, stop_id), [])
        )
    )
    stop_times = MagicMock()
    stop_times.get_stop_departures = AsyncMock(return_value=list(scheduled_rows))
    stop_times.get_stop_service_keys = AsyncMock(return_value=list(service_keys))
    trips = MagicMock()
    trips.get_trip_headsigns = AsyncMock(return_value=list(headsign_rows))
    stops = MagicMock()
    stops.get_sibling_stop_ids = AsyncMock(return_value=list(sibling_ids))
    feed = StopDepartureFeed(stop_updates, stop_times, trips, stops)
    return feed, stop_updates, stop_times, trips, stops


async def test_gathers_every_platform_sharing_the_name_in_the_city():
    feed, _, stop_times, _, stops = _feed(sibling_ids=("s1", "s2", "s3"))

    await feed.get_departures(_selection())

    stops.get_sibling_stop_ids.assert_awaited_once_with("s1")
    assert stop_times.get_stop_departures.await_args.kwargs["stop_ids"] == [
        "s1",
        "s2",
        "s3",
    ]


async def test_falls_back_to_the_tapped_stop_when_it_has_no_siblings():
    feed, _, stop_times, _, _ = _feed(sibling_ids=())

    await feed.get_departures(_selection())

    assert stop_times.get_stop_departures.await_args.kwargs["stop_ids"] == ["s1"]


async def test_the_schedule_is_no_longer_filtered_by_route():
    feed, _, stop_times, _, _ = _feed()

    await feed.get_departures(_selection())

    assert "route_id" not in stop_times.get_stop_departures.await_args.kwargs


async def test_departures_span_every_route_serving_the_stop():
    feed, _, _, _, _ = _feed(
        scheduled_rows=[
            _scheduled_row("t1", "08:00:00", route_id="r1", headsign="Mosson"),
            _scheduled_row("t2", "08:01:00", route_id="r2", headsign="Odysseum"),
            _scheduled_row("t3", "08:02:00", route_id="r3", headsign="Jacou"),
        ]
    )

    departures = await feed.get_departures(_selection())

    assert {departure.route_id for departure in departures} == {"r1", "r2", "r3"}
    assert {departure.headsign for departure in departures} == {
        "Mosson",
        "Odysseum",
        "Jacou",
    }


async def test_scheduled_departures_carry_their_line_identity():
    feed, _, _, _, _ = _feed(
        scheduled_rows=[_scheduled_row("t1", "08:00:00", short_name="4")]
    )

    departure = (await feed.get_departures(_selection()))[0]

    assert departure.route_short_name == "4"
    assert departure.route_color == "005CA9"
    assert departure.route_type == 0
    assert departure.is_realtime is False


async def test_realtime_is_polled_for_every_route_direction_platform():
    feed, stop_updates, _, _, _ = _feed(
        sibling_ids=("s1", "s2"),
        service_keys=[
            _service_key("r1", 0, "s1"),
            _service_key("r1", 1, "s2"),
            _service_key("r2", 0, "s1"),
        ],
    )

    await feed.get_departures(_selection())

    polled = {
        (c.kwargs["route_id"], c.kwargs["direction_id"], c.kwargs["stop_id"])
        for c in stop_updates.get_stop_updates.await_args_list
    }
    assert polled == {("r1", 0, "s1"), ("r1", 1, "s2"), ("r2", 0, "s1")}


async def test_realtime_borrows_line_identity_from_the_schedule():
    feed, _, _, _, _ = _feed(
        realtime_by_key={("r2", 0, "s1"): [_stop_update("t9", 120)]},
        service_keys=[_service_key("r2", 0, "s1")],
        scheduled_rows=[
            _scheduled_row("t1", "08:00:00", route_id="r2", short_name="7")
        ],
        headsign_rows=[SimpleNamespace(id="t9", direction_id=0, headsign="Jacou")],
    )

    live = [d for d in await feed.get_departures(_selection()) if d.is_realtime][0]

    assert live.route_short_name == "7"
    assert live.route_color == "005CA9"
    assert live.headsign == "Jacou"


async def test_realtime_falls_back_when_the_route_is_absent_from_the_schedule():
    feed, _, _, _, _ = _feed(
        realtime_by_key={("r9", 0, "s1"): [_stop_update("t9", 120)]},
        service_keys=[_service_key("r9", 0, "s1")],
        headsign_rows=[SimpleNamespace(id="t9", direction_id=0, headsign="Ailleurs")],
    )

    departure = (await feed.get_departures(_selection()))[0]

    assert departure.route_short_name == "r9"
    assert departure.route_color is None
    assert departure.route_type == 3


async def test_a_trip_seen_live_is_not_repeated_from_the_schedule():
    feed, _, _, _, _ = _feed(
        realtime_by_key={("r1", 0, "s1"): [_stop_update("t1", 120)]},
        service_keys=[_service_key("r1", 0, "s1")],
        scheduled_rows=[_scheduled_row("t1", "23:59:00")],
        headsign_rows=[SimpleNamespace(id="t1", direction_id=0, headsign="Mosson")],
    )

    departures = await feed.get_departures(_selection())

    assert [departure.trip_id for departure in departures] == ["t1"]
    assert departures[0].is_realtime is True


async def test_stale_realtime_departures_are_dropped():
    stale = StopUpdate(
        trip_id="old",
        timestamp=_NOW - 3600,
        departure_time=_NOW - 3600,
        departure_delay=0,
        arrival_time=_NOW - 3600,
        arrival_delay=0,
    )
    feed, _, _, _, _ = _feed(
        realtime_by_key={("r1", 0, "s1"): [stale]},
        service_keys=[_service_key()],
    )

    assert await feed.get_departures(_selection()) == []


async def test_no_headsign_lookup_without_realtime_departures():
    feed, _, _, trips, _ = _feed(service_keys=[_service_key()])

    await feed.get_departures(_selection())

    trips.get_trip_headsigns.assert_not_awaited()


async def test_limit_applies_per_destination_so_no_line_crowds_out_another():
    feed, _, _, _, _ = _feed(
        scheduled_rows=[
            _scheduled_row(f"a{i}", f"08:0{i}:00", route_id="r1", headsign="Mosson")
            for i in range(5)
        ]
        + [_scheduled_row("z", "09:00:00", route_id="r2", headsign="Odysseum")]
    )

    departures = await feed.get_departures(_selection(limit=2))

    by_destination = {}
    for departure in departures:
        by_destination.setdefault(departure.headsign, []).append(departure)

    assert len(by_destination["Mosson"]) == 2
    assert len(by_destination["Odysseum"]) == 1


async def test_two_headsigns_on_one_route_are_separate_destinations():
    feed, _, _, _, _ = _feed(
        scheduled_rows=[
            _scheduled_row("a", "08:00:00", headsign="Mosson"),
            _scheduled_row("b", "08:01:00", headsign="Jacou"),
        ]
    )

    departures = await feed.get_departures(_selection(limit=1))

    assert {departure.headsign for departure in departures} == {"Mosson", "Jacou"}


async def test_departures_are_returned_soonest_first():
    feed, _, _, _, _ = _feed(
        scheduled_rows=[
            _scheduled_row("late", "09:00:00", route_id="r1", headsign="Mosson"),
            _scheduled_row("soon", "08:00:00", route_id="r2", headsign="Odysseum"),
        ]
    )

    departures = await feed.get_departures(_selection())

    assert [departure.trip_id for departure in departures] == ["soon", "late"]


async def test_an_empty_stop_yields_no_departures():
    feed, _, _, _, _ = _feed()

    assert await feed.get_departures(_selection()) == []
