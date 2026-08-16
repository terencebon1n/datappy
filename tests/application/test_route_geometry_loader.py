from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

from backend.application.services.api.route_geometry_loader import (
    RouteGeometryLoaderService,
)


def _shape_row(direction_id: int, latitude: float, longitude: float):
    return SimpleNamespace(
        direction_id=direction_id, latitude=latitude, longitude=longitude
    )


def _stop_row(stop_id: str, name: str, wheelchair_boarding: int | None = 1):
    return SimpleNamespace(
        id=stop_id,
        name=name,
        latitude=43.6,
        longitude=3.87,
        code="1234",
        platform_code="B",
        wheelchair_boarding=wheelchair_boarding,
    )


def _headsign_row(direction_id: int, headsign: str):
    return SimpleNamespace(direction_id=direction_id, headsign=headsign)


def _service(shape_rows, stop_rows, headsign_rows=()):
    shapes = MagicMock()
    shapes.get_route_shapes = AsyncMock(return_value=shape_rows)
    stops = MagicMock()
    stops.get_route_stops = AsyncMock(return_value=stop_rows)
    trips = MagicMock()
    trips.get_direction_headsigns = AsyncMock(return_value=list(headsign_rows))
    return RouteGeometryLoaderService(shapes, stops, trips), shapes, stops, trips


async def test_groups_points_into_one_polyline_per_direction():
    service, _, _, _ = _service(
        [
            _shape_row(0, 43.60, 3.87),
            _shape_row(0, 43.61, 3.88),
            _shape_row(1, 43.61, 3.88),
            _shape_row(1, 43.60, 3.87),
        ],
        [],
    )

    geometry = await service.get_route_geometry("r1")

    assert [shape.direction_id for shape in geometry.shapes] == [0, 1]
    assert len(geometry.shapes[0].points) == 2
    assert geometry.shapes[0].points[0].latitude == 43.60


async def test_preserves_the_row_order_within_a_direction():
    service, _, _, _ = _service(
        [
            _shape_row(0, 43.60, 3.87),
            _shape_row(0, 43.61, 3.88),
            _shape_row(0, 43.62, 3.89),
        ],
        [],
    )

    geometry = await service.get_route_geometry("r1")

    assert [point.latitude for point in geometry.shapes[0].points] == [
        43.60,
        43.61,
        43.62,
    ]


async def test_directions_are_ordered_even_when_rows_are_not():
    service, _, _, _ = _service(
        [_shape_row(1, 43.6, 3.87), _shape_row(0, 43.6, 3.87)], []
    )

    geometry = await service.get_route_geometry("r1")

    assert [shape.direction_id for shape in geometry.shapes] == [0, 1]


async def test_maps_route_stops_with_their_metadata():
    service, _, stops, _ = _service([], [_stop_row("s1", "Comédie")])

    geometry = await service.get_route_geometry("r1")

    assert geometry.stops[0].id == "s1"
    assert geometry.stops[0].name == "Comédie"
    assert geometry.stops[0].latitude == 43.6
    assert geometry.stops[0].code == "1234"
    assert geometry.stops[0].platform_code == "B"
    assert geometry.stops[0].wheelchair_boarding == 1
    stops.get_route_stops.assert_awaited_once_with("r1")


async def test_stop_metadata_may_be_absent():
    service, _, _, _ = _service(
        [], [_stop_row("s1", "Comédie", wheelchair_boarding=None)]
    )

    geometry = await service.get_route_geometry("r1")

    assert geometry.stops[0].wheelchair_boarding is None


async def test_maps_direction_headsigns():
    service, _, _, trips = _service(
        [], [], [_headsign_row(0, "Mosson"), _headsign_row(1, "Odysseum")]
    )

    geometry = await service.get_route_geometry("r1")

    assert [h.headsign for h in geometry.direction_headsigns] == [
        "Mosson",
        "Odysseum",
    ]
    trips.get_direction_headsigns.assert_awaited_once_with("r1")


async def test_queries_every_repository_with_the_route_id():
    service, shapes, stops, trips = _service([], [])

    await service.get_route_geometry("r42")

    shapes.get_route_shapes.assert_awaited_once_with("r42")
    stops.get_route_stops.assert_awaited_once_with("r42")
    trips.get_direction_headsigns.assert_awaited_once_with("r42")


async def test_a_route_without_geometry_yields_empty_lists():
    service, _, _, _ = _service([], [])

    geometry = await service.get_route_geometry("r1")

    assert geometry.shapes == []
    assert geometry.stops == []
    assert geometry.direction_headsigns == []
