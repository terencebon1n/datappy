from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

from backend.application.dto.trip import PathDTO
from backend.application.services.api.route_loader import RouteLoaderService
from backend.application.services.api.stop_loader import StopLoaderService
from backend.application.services.api.trip_loader import TripLoaderService
from backend.domain.enums import route_type_name


async def test_route_loader_maps_conveyances_and_type_names():
    repo = MagicMock()
    repo.get_conveyances = AsyncMock(
        return_value=[
            SimpleNamespace(
                id="r1", short_name="1", long_name="L1", color="FF0000", type=0
            ),
            SimpleNamespace(
                id="r2", short_name="2", long_name="L2", color="00FF00", type=999
            ),
        ]
    )
    service = RouteLoaderService(repo)

    result = await service.get_conveyances()

    assert result[0].type_name == "Tram"  # known GTFS type
    assert result[1].type_name == "Autre"  # unknown type -> fallback


def test_route_type_name_helper():
    assert route_type_name(3) == "Bus"
    assert route_type_name(12345) == "Autre"


async def test_stop_loader_maps_names():
    repo = MagicMock()
    repo.get_stop_names = AsyncMock(return_value=["Gare", "Comédie"])
    service = StopLoaderService(repo)

    result = await service.get_stop_names("r1")

    assert [dto.name for dto in result] == ["Gare", "Comédie"]
    repo.get_stop_names.assert_awaited_once_with("r1")


async def test_trip_loader_builds_direction_dto():
    repo = MagicMock()
    repo.get_direction = AsyncMock(
        return_value={
            "direction_id": 1,
            "stop_id__origin": "a",
            "stop_id__destination": "b",
        }
    )
    service = TripLoaderService(repo)

    result = await service.get_direction(
        PathDTO(route_id="r1", stop_name__origin="A", stop_name__destination="B")
    )

    assert result.direction_id == 1
    repo.get_direction.assert_awaited_once_with(
        route_id="r1", origin_name="A", destination_name="B"
    )
