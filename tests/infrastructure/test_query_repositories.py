"""Async read repositories — SQLAlchemy queries are built for real; the session
execution is mocked so no database is required."""

from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest

from backend.domain.gtfs.geo import Coordinates
from backend.infrastructure.database.postgres.repositories.route import RouteRepository
from backend.infrastructure.database.postgres.repositories.shape import ShapeRepository
from backend.infrastructure.database.postgres.repositories.stop import StopRepository
from backend.infrastructure.database.postgres.repositories.stop_time import (
    StopTimeRepository,
)
from backend.infrastructure.database.postgres.repositories.trip import TripRepository


def _session_returning(result: MagicMock) -> MagicMock:
    session = MagicMock()
    session.execute = AsyncMock(return_value=result)
    return session


async def test_route_get_conveyances():
    result = MagicMock()
    result.all.return_value = [
        SimpleNamespace(id="r1", short_name="1", long_name="L1", color="c", type=0)
    ]
    repo = RouteRepository(_session_returning(result))

    rows = await repo.get_conveyances()

    assert rows[0].id == "r1"


async def test_stop_get_stop_names():
    result = MagicMock()
    result.scalars.return_value.all.return_value = ["Gare", "Comédie"]
    repo = StopRepository(_session_returning(result))

    assert await repo.get_stop_names("r1") == ["Gare", "Comédie"]


async def test_stop_get_nearby_stops():
    result = MagicMock()
    result.all.return_value = [
        SimpleNamespace(
            name="Comédie",
            latitude=43.6,
            longitude=3.87,
            route_id="r1",
            short_name="1",
            long_name="L1",
            color="c",
            type=0,
        )
    ]
    session = _session_returning(result)
    repo = StopRepository(session)
    box = Coordinates(latitude=43.6, longitude=3.87).bounding_box(800)

    rows = await repo.get_nearby_stops(box)

    assert rows[0].name == "Comédie"
    compiled = str(session.execute.await_args.args[0])
    assert "stop.latitude BETWEEN" in compiled
    assert "stop.longitude BETWEEN" in compiled
    assert "DISTINCT" in compiled


async def test_stop_time_get_reachable_trip_ids():
    result = MagicMock()
    result.scalars.return_value.all.return_value = ["t1", "t2"]
    repo = StopTimeRepository(_session_returning(result))

    assert await repo.get_reachable_trip_ids(["t1", "t2", "t3"], "dest") == ["t1", "t2"]


async def test_stop_time_get_scheduled_departures():
    result = MagicMock()
    result.all.return_value = [
        SimpleNamespace(
            trip_id="t1", departure_time="08:00:00", arrival_time="08:05:00"
        )
    ]
    repo = StopTimeRepository(_session_returning(result))

    departures = await repo.get_scheduled_departures(
        route_id="r1",
        direction_id=0,
        origin_stop_id="o",
        destination_stop_id="d",
        after_clock="07:00:00",
        service_date="20260706",
        weekday="monday",
        limit=5,
    )

    assert departures[0].trip_id == "t1"
    assert departures[0].departure_time == "08:00:00"


async def test_trip_get_direction_found():
    result = MagicMock()
    result.all.return_value = [
        SimpleNamespace(direction_id=1, origin_stop_id="o", destination_stop_id="d")
    ]
    repo = TripRepository(_session_returning(result))

    direction = await repo.get_direction("r1", "Origin", "Dest")

    assert direction == {
        "direction_id": 1,
        "stop_id__origin": "o",
        "stop_id__destination": "d",
    }


async def test_trip_get_direction_not_found_raises():
    result = MagicMock()
    result.all.return_value = []
    repo = TripRepository(_session_returning(result))

    with pytest.raises(Exception, match="No direction found"):
        await repo.get_direction("r1", "Origin", "Dest")


async def test_shape_get_route_shapes_picks_the_longest_per_direction():
    result = MagicMock()
    result.all.return_value = [
        SimpleNamespace(direction_id=0, latitude=43.6, longitude=3.87)
    ]
    session = _session_returning(result)
    repo = ShapeRepository(session)

    rows = await repo.get_route_shapes("r1")

    assert rows[0].direction_id == 0
    compiled = str(session.execute.await_args.args[0])
    assert "row_number() OVER" in compiled
    assert "count(*)" in compiled
    assert "ORDER BY" in compiled


async def test_stop_get_route_stops():
    result = MagicMock()
    result.all.return_value = [
        SimpleNamespace(id="s1", name="Comédie", latitude=43.6, longitude=3.87)
    ]
    session = _session_returning(result)
    repo = StopRepository(session)

    rows = await repo.get_route_stops("r1")

    assert rows[0].name == "Comédie"
    compiled = str(session.execute.await_args.args[0])
    assert "DISTINCT" in compiled
    assert "trip.route_id" in compiled


async def test_stop_time_get_stop_departures():
    result = MagicMock()
    result.all.return_value = [
        SimpleNamespace(
            trip_id="t1",
            departure_time="08:00:00",
            direction_id=0,
            headsign="Mosson",
        )
    ]
    session = _session_returning(result)
    repo = StopTimeRepository(session)

    rows = await repo.get_stop_departures(
        route_id="r1",
        stop_id="s1",
        after_clock="07:00:00",
        service_date="20260706",
        weekday="monday",
        limit=6,
    )

    assert rows[0].headsign == "Mosson"
    compiled = str(session.execute.await_args.args[0])
    assert "trip.headsign" in compiled
    assert "trip.direction_id" in compiled
    assert "EXCEPT" in compiled


async def test_trip_get_trip_headsigns():
    result = MagicMock()
    result.all.return_value = [
        SimpleNamespace(id="t1", direction_id=0, headsign="Mosson")
    ]
    session = _session_returning(result)
    repo = TripRepository(session)

    rows = await repo.get_trip_headsigns(["t1", "t2"])

    assert rows[0].headsign == "Mosson"
    assert "IN " in str(session.execute.await_args.args[0])


async def test_trip_get_direction_headsigns_keeps_the_most_common():
    result = MagicMock()
    result.all.return_value = [
        SimpleNamespace(direction_id=0, headsign="Mosson"),
        SimpleNamespace(direction_id=1, headsign="Odysseum"),
    ]
    session = _session_returning(result)
    repo = TripRepository(session)

    rows = await repo.get_direction_headsigns("r1")

    assert [row.headsign for row in rows] == ["Mosson", "Odysseum"]
    compiled = str(session.execute.await_args.args[0])
    assert "row_number() OVER" in compiled
    assert "count(*)" in compiled


async def test_stop_get_route_stops_selects_metadata():
    result = MagicMock()
    result.all.return_value = []
    session = _session_returning(result)

    await StopRepository(session).get_route_stops("r1")

    compiled = str(session.execute.await_args.args[0])
    assert "stop.code" in compiled
    assert "stop.platform_code" in compiled
    assert "stop.wheelchair_boarding" in compiled
