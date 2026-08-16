from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

from backend.application.dto.stop import NearbyQueryDTO
from backend.application.services.api.nearby_stop_loader import NearbyStopLoaderService

_LATITUDE = 43.608490
_LONGITUDE = 3.879568


def _query(radius_m: int = 800, limit: int = 10) -> NearbyQueryDTO:
    return NearbyQueryDTO(
        latitude=_LATITUDE, longitude=_LONGITUDE, radius_m=radius_m, limit=limit
    )


def _row(
    name: str,
    latitude: float,
    longitude: float,
    route_id: str = "r1",
    short_name: str = "1",
    route_type: int = 0,
):
    return SimpleNamespace(
        name=name,
        latitude=latitude,
        longitude=longitude,
        route_id=route_id,
        short_name=short_name,
        long_name=f"Ligne {short_name}",
        color="005CA9",
        type=route_type,
    )


def _service(rows):
    repo = MagicMock()
    repo.get_nearby_stops = AsyncMock(return_value=rows)
    return NearbyStopLoaderService(repo), repo


async def test_returns_stops_ordered_by_distance():
    service, _ = _service(
        [
            _row("Gare Saint-Roch", 43.604900, 3.880600),
            _row("Comédie", 43.608490, 3.879568),
        ]
    )

    result = await service.get_nearby_stops(_query())

    assert [stop.name for stop in result] == ["Comédie", "Gare Saint-Roch"]
    assert result[0].distance_m == 0
    assert result[1].distance_m == 408


async def test_queries_the_repository_with_the_bounding_box_for_the_radius():
    service, repo = _service([])

    await service.get_nearby_stops(_query(radius_m=500))

    box = repo.get_nearby_stops.await_args.args[0]
    assert box.min_latitude < _LATITUDE < box.max_latitude
    assert box.min_longitude < _LONGITUDE < box.max_longitude


async def test_platforms_sharing_a_name_collapse_into_one_stop():
    service, _ = _service(
        [
            _row("Comédie", 43.608700, 3.879568, route_id="r2", short_name="2"),
            _row("Comédie", 43.608490, 3.879568, route_id="r1", short_name="1"),
        ]
    )

    result = await service.get_nearby_stops(_query())

    assert len(result) == 1
    assert [route.short_name for route in result[0].routes] == ["1", "2"]


async def test_collapsed_stop_keeps_the_nearest_platform_position():
    service, _ = _service(
        [
            _row("Comédie", 43.610000, 3.879568),
            _row("Comédie", 43.608490, 3.879568, route_id="r2", short_name="2"),
        ]
    )

    result = await service.get_nearby_stops(_query())

    assert result[0].distance_m == 0
    assert result[0].latitude == 43.608490


async def test_repeated_route_at_one_stop_is_listed_once():
    service, _ = _service(
        [
            _row("Comédie", 43.608490, 3.879568),
            _row("Comédie", 43.608495, 3.879568),
        ]
    )

    result = await service.get_nearby_stops(_query())

    assert [route.id for route in result[0].routes] == ["r1"]


async def test_routes_are_ordered_by_type_then_short_name():
    service, _ = _service(
        [
            _row(
                "Comédie",
                43.608490,
                3.879568,
                route_id="b7",
                short_name="7",
                route_type=3,
            ),
            _row(
                "Comédie",
                43.608490,
                3.879568,
                route_id="t4",
                short_name="4",
                route_type=0,
            ),
            _row(
                "Comédie",
                43.608490,
                3.879568,
                route_id="b2",
                short_name="2",
                route_type=3,
            ),
        ]
    )

    result = await service.get_nearby_stops(_query())

    assert [route.short_name for route in result[0].routes] == ["4", "2", "7"]


async def test_stops_inside_the_bounding_box_but_beyond_the_radius_are_dropped():
    service, _ = _service(
        [
            _row("Comédie", 43.608490, 3.879568),
            _row("Gare Saint-Roch", 43.604900, 3.880600),
        ]
    )

    result = await service.get_nearby_stops(_query(radius_m=200))

    assert [stop.name for stop in result] == ["Comédie"]


async def test_limit_caps_the_number_of_stops():
    service, _ = _service(
        [
            _row("Comédie", 43.608490, 3.879568),
            _row("Gare Saint-Roch", 43.604900, 3.880600),
        ]
    )

    result = await service.get_nearby_stops(_query(limit=1))

    assert [stop.name for stop in result] == ["Comédie"]


async def test_equidistant_stops_are_ordered_by_name():
    service, _ = _service(
        [
            _row("Saint-Denis", 43.608490, 3.879568),
            _row("Albert 1er", 43.608490, 3.879568),
        ]
    )

    result = await service.get_nearby_stops(_query())

    assert [stop.name for stop in result] == ["Albert 1er", "Saint-Denis"]


async def test_route_type_name_is_resolved():
    service, _ = _service(
        [
            _row("Comédie", 43.608490, 3.879568, route_type=3),
            _row(
                "Comédie",
                43.608490,
                3.879568,
                route_id="x",
                short_name="X",
                route_type=999,
            ),
        ]
    )

    result = await service.get_nearby_stops(_query())

    assert [route.type_name for route in result[0].routes] == ["Bus", "Autre"]


async def test_no_rows_yields_no_stops():
    service, _ = _service([])

    assert await service.get_nearby_stops(_query()) == []
