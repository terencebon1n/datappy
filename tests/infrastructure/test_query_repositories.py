"""Async read repositories — SQLAlchemy queries are built for real; the session
execution is mocked so no database is required."""

from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest

from backend.infrastructure.database.postgres.repositories.route import RouteRepository
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
        SimpleNamespace(
            direction_id=1, origin_stop_id="o", destination_stop_id="d"
        )
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
