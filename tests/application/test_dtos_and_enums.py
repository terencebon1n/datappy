from backend.application.dto.route import ConveyanceDTO, RouteIdDTO
from backend.application.dto.stop import StopNameDTO, TransitPathDTO
from backend.application.dto.trip import DirectionDTO, PathDTO
from backend.application.services.enums import ServiceCommand
from backend.domain.gtfs_rt.enums import City


def test_route_dtos():
    assert RouteIdDTO(route_id="r1").route_id == "r1"
    conv = ConveyanceDTO(
        id="r1",
        short_name="1",
        long_name="Line 1",
        color="FF0000",
        type=0,
        type_name="Tram",
    )
    assert conv.type_name == "Tram"


def test_stop_dtos():
    assert StopNameDTO(name="Gare").name == "Gare"
    path = TransitPathDTO(
        city=City.MONTPELLIER,
        route_id="r1",
        direction_id=0,
        stop_id__origin="a",
        stop_id__destination="b",
    )
    assert path.city == City.MONTPELLIER
    assert path.stop_id__destination == "b"


def test_trip_dtos():
    path = PathDTO(
        route_id="r1", stop_name__origin="A", stop_name__destination="B"
    )
    assert path.stop_name__origin == "A"
    direction = DirectionDTO(
        direction_id=1, stop_id__origin="a", stop_id__destination="b"
    )
    assert direction.direction_id == 1


def test_service_command_enum():
    assert ServiceCommand.API == "api"
    assert {c.value for c in ServiceCommand} == {
        "api",
        "consumer",
        "producer",
        "populate",
        "diagram",
    }
