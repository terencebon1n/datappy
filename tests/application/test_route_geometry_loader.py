from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

from backend.application.services.api.route_geometry_loader import (
    RouteGeometryLoaderService,
)


def _shape_row(direction_id: int, latitude: float, longitude: float):
    return SimpleNamespace(
        direction_id=direction_id, latitude=latitude, longitude=longitude
    )


def _stop_row(stop_id: str, name: str):
    return SimpleNamespace(id=stop_id, name=name, latitude=43.6, longitude=3.87)


def _service(shape_rows, stop_rows):
    shapes = MagicMock()
    shapes.get_route_shapes = AsyncMock(return_value=shape_rows)
    stops = MagicMock()
    stops.get_route_stops = AsyncMock(return_value=stop_rows)
    return RouteGeometryLoaderService(shapes, stops), shapes, stops


async def test_groups_points_into_one_polyline_per_direction():
    service, _, _ = _service(
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
    service, _, _ = _service(
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
    service, _, _ = _service([_shape_row(1, 43.6, 3.87), _shape_row(0, 43.6, 3.87)], [])

    geometry = await service.get_route_geometry("r1")

    assert [shape.direction_id for shape in geometry.shapes] == [0, 1]


async def test_maps_route_stops():
    service, _, stops = _service([], [_stop_row("s1", "Comédie")])

    geometry = await service.get_route_geometry("r1")

    assert geometry.stops[0].id == "s1"
    assert geometry.stops[0].name == "Comédie"
    assert geometry.stops[0].latitude == 43.6
    stops.get_route_stops.assert_awaited_once_with("r1")


async def test_queries_both_repositories_with_the_route_id():
    service, shapes, stops = _service([], [])

    await service.get_route_geometry("r42")

    shapes.get_route_shapes.assert_awaited_once_with("r42")
    stops.get_route_stops.assert_awaited_once_with("r42")


async def test_a_route_without_geometry_yields_empty_lists():
    service, _, _ = _service([], [])

    geometry = await service.get_route_geometry("r1")

    assert geometry.shapes == []
    assert geometry.stops == []
