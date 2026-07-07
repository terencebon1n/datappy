from unittest.mock import AsyncMock, MagicMock

from backend.api.dependencies import (
    get_route_loader,
    get_stop_loader,
    get_trip_loader,
)
from backend.application.dto.route import ConveyanceDTO
from backend.application.dto.stop import StopNameDTO
from backend.application.dto.trip import DirectionDTO

_CITY_HEADER = {"city": "montpellier"}


def test_get_cities(client):
    response = client.get("/city")
    assert response.status_code == 200
    assert "montpellier" in response.json()


def test_get_conveyances(app, client):
    loader = MagicMock()
    loader.get_conveyances = AsyncMock(
        return_value=[
            ConveyanceDTO(
                id="r1",
                short_name="1",
                long_name="L1",
                color="FF0000",
                type=0,
                type_name="Tram",
            )
        ]
    )
    app.dependency_overrides[get_route_loader] = lambda: loader

    response = client.get("/conveyance", headers=_CITY_HEADER)

    assert response.status_code == 200
    assert response.json()[0]["id"] == "r1"


def test_get_conveyances_requires_city_header(client):
    response = client.get("/conveyance")
    assert response.status_code == 400


def test_get_stops(app, client):
    loader = MagicMock()
    loader.get_stop_names = AsyncMock(return_value=[StopNameDTO(name="Gare")])
    app.dependency_overrides[get_stop_loader] = lambda: loader

    response = client.get("/stop", params={"route_id": "r1"}, headers=_CITY_HEADER)

    assert response.status_code == 200
    assert response.json() == [{"name": "Gare"}]


def test_get_direction(app, client):
    loader = MagicMock()
    loader.get_direction = AsyncMock(
        return_value=DirectionDTO(
            direction_id=1, stop_id__origin="a", stop_id__destination="b"
        )
    )
    app.dependency_overrides[get_trip_loader] = lambda: loader

    response = client.get(
        "/direction",
        params={
            "route_id": "r1",
            "stop_name__origin": "A",
            "stop_name__destination": "B",
        },
        headers=_CITY_HEADER,
    )

    assert response.status_code == 200
    assert response.json()["direction_id"] == 1
