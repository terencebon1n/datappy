from unittest.mock import AsyncMock, MagicMock

import pytest

from backend.api.dependencies import (
    get_alert_feed,
    get_nearby_stop_loader,
    get_route_geometry_loader,
    get_route_loader,
    get_stop_departure_feed,
    get_stop_loader,
    get_trip_loader,
)
from backend.application.dto.departure import StopDepartureDTO
from backend.application.dto.geometry import (
    DirectionHeadsignDTO,
    PointDTO,
    RouteGeometryDTO,
    RouteShapeDTO,
    RouteStopDTO,
)
from backend.application.dto.route import ConveyanceDTO
from backend.application.dto.stop import NearbyStopDTO, StopNameDTO
from backend.application.dto.trip import DirectionDTO
from backend.domain.gtfs_rt.alert import Alert, InformedEntity
from backend.domain.gtfs_rt.enums import AlertCause, AlertEffect, AlertSeverity

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


def test_get_nearby_stops(app, client):
    loader = MagicMock()
    loader.get_nearby_stops = AsyncMock(
        return_value=[
            NearbyStopDTO(
                name="Comédie",
                distance_m=124,
                latitude=43.6085,
                longitude=3.8794,
                routes=[
                    ConveyanceDTO(
                        id="r1",
                        short_name="1",
                        long_name="L1",
                        color="FF0000",
                        type=0,
                        type_name="Tram",
                    )
                ],
            )
        ]
    )
    app.dependency_overrides[get_nearby_stop_loader] = lambda: loader

    response = client.get(
        "/nearby-stops",
        params={"latitude": 43.6085, "longitude": 3.8794, "radius_m": 500},
        headers=_CITY_HEADER,
    )

    assert response.status_code == 200
    body = response.json()
    assert body[0]["name"] == "Comédie"
    assert body[0]["distance_m"] == 124
    assert body[0]["routes"][0]["short_name"] == "1"
    assert loader.get_nearby_stops.await_args.args[0].radius_m == 500


def test_get_nearby_stops_requires_city_header(client):
    response = client.get(
        "/nearby-stops", params={"latitude": 43.6085, "longitude": 3.8794}
    )
    assert response.status_code == 400


@pytest.mark.parametrize(
    "params",
    [
        {"longitude": 3.8794},
        {"latitude": 91.0, "longitude": 3.8794},
        {"latitude": 43.6085, "longitude": 181.0},
        {"latitude": 43.6085, "longitude": 3.8794, "radius_m": 0},
        {"latitude": 43.6085, "longitude": 3.8794, "radius_m": 99999},
        {"latitude": 43.6085, "longitude": 3.8794, "limit": 0},
    ],
)
def test_get_nearby_stops_rejects_invalid_query(app, client, params):
    loader = MagicMock()
    loader.get_nearby_stops = AsyncMock(return_value=[])
    app.dependency_overrides[get_nearby_stop_loader] = lambda: loader

    response = client.get("/nearby-stops", params=params, headers=_CITY_HEADER)

    assert response.status_code == 422
    loader.get_nearby_stops.assert_not_awaited()


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


def test_get_alerts(app, client):
    feed = MagicMock()
    feed.get_alerts = AsyncMock(
        return_value=[
            Alert(
                id="a1",
                cause=AlertCause.STRIKE,
                effect=AlertEffect.NO_SERVICE,
                severity=AlertSeverity.SEVERE,
                header_text="Grève",
                description_text="Aucun service",
                url="https://info.fr",
                informed_entities=[InformedEntity(route_id="r1")],
            )
        ]
    )
    app.dependency_overrides[get_alert_feed] = lambda: feed

    response = client.get(
        "/alerts",
        params={
            "city": "montpellier",
            "route_id": "r1",
            "direction_id": 0,
            "stop_id": "s1",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body[0]["id"] == "a1"
    assert body[0]["severity"] == "SEVERE"
    assert body[0]["header_text"] == "Grève"
    assert body[0]["url"] == "https://info.fr"
    # the informed entities stay server-side, they are a filtering concern
    assert "informed_entities" not in body[0]

    selection = feed.get_alerts.await_args.args[0]
    assert selection.route_id == "r1"
    assert selection.direction_id == 0
    assert selection.stop_id == "s1"


def test_get_alerts_without_stop_or_direction(app, client):
    feed = MagicMock()
    feed.get_alerts = AsyncMock(return_value=[])
    app.dependency_overrides[get_alert_feed] = lambda: feed

    response = client.get("/alerts", params={"city": "montpellier", "route_id": "r1"})

    assert response.status_code == 200
    assert response.json() == []
    selection = feed.get_alerts.await_args.args[0]
    assert selection.direction_id is None
    assert selection.stop_id is None


def test_get_alerts_requires_route_id(client):
    response = client.get("/alerts", params={"city": "montpellier"})
    assert response.status_code == 422


def test_get_route_geometry(app, client):
    loader = MagicMock()
    loader.get_route_geometry = AsyncMock(
        return_value=RouteGeometryDTO(
            shapes=[
                RouteShapeDTO(
                    direction_id=0,
                    points=[
                        PointDTO(latitude=43.60, longitude=3.87),
                        PointDTO(latitude=43.61, longitude=3.88),
                    ],
                )
            ],
            stops=[
                RouteStopDTO(
                    id="s1",
                    name="Comédie",
                    latitude=43.6085,
                    longitude=3.8794,
                    code="1234",
                    platform_code="B",
                    wheelchair_boarding=1,
                )
            ],
            direction_headsigns=[
                DirectionHeadsignDTO(direction_id=0, headsign="Mosson")
            ],
        )
    )
    app.dependency_overrides[get_route_geometry_loader] = lambda: loader

    response = client.get(
        "/route-geometry", params={"route_id": "r1"}, headers=_CITY_HEADER
    )

    assert response.status_code == 200
    body = response.json()
    assert body["shapes"][0]["direction_id"] == 0
    assert len(body["shapes"][0]["points"]) == 2
    assert body["stops"][0]["name"] == "Comédie"
    assert body["stops"][0]["platform_code"] == "B"
    assert body["stops"][0]["wheelchair_boarding"] == 1
    assert body["direction_headsigns"][0]["headsign"] == "Mosson"
    loader.get_route_geometry.assert_awaited_once_with("r1")


def test_get_route_geometry_requires_city_header(client):
    response = client.get("/route-geometry", params={"route_id": "r1"})
    assert response.status_code == 400


def test_get_route_geometry_requires_route_id(app, client):
    loader = MagicMock()
    loader.get_route_geometry = AsyncMock(return_value=None)
    app.dependency_overrides[get_route_geometry_loader] = lambda: loader

    response = client.get("/route-geometry", headers=_CITY_HEADER)

    assert response.status_code == 422
    loader.get_route_geometry.assert_not_awaited()


def test_get_stop_departures(app, client):
    feed = MagicMock()
    feed.get_departures = AsyncMock(
        return_value=[
            StopDepartureDTO(
                trip_id="t1",
                route_id="r1",
                route_short_name="1",
                route_color="005CA9",
                route_type=0,
                direction_id=0,
                headsign="Mosson",
                departure_time=1700000000,
                departure_delay=30,
                is_realtime=True,
            )
        ]
    )
    app.dependency_overrides[get_stop_departure_feed] = lambda: feed

    response = client.get(
        "/stop-departures",
        params={"city": "montpellier", "stop_id": "s1", "limit": 4},
        headers=_CITY_HEADER,
    )

    assert response.status_code == 200
    body = response.json()
    assert body[0]["headsign"] == "Mosson"
    assert body[0]["route_short_name"] == "1"
    assert body[0]["is_realtime"] is True
    assert feed.get_departures.await_args.args[0].limit == 4


def test_get_stop_departures_defaults_the_limit(app, client):
    feed = MagicMock()
    feed.get_departures = AsyncMock(return_value=[])
    app.dependency_overrides[get_stop_departure_feed] = lambda: feed

    response = client.get(
        "/stop-departures",
        params={"city": "montpellier", "stop_id": "s1"},
        headers=_CITY_HEADER,
    )

    assert response.status_code == 200
    assert feed.get_departures.await_args.args[0].limit == 4


@pytest.mark.parametrize(
    "params",
    [
        {"city": "montpellier"},
        {"stop_id": "s1"},
        {"city": "nowhere", "stop_id": "s1"},
        {"city": "montpellier", "stop_id": "s1", "limit": 0},
        {"city": "montpellier", "stop_id": "s1", "limit": 99},
    ],
)
def test_get_stop_departures_rejects_invalid_query(app, client, params):
    feed = MagicMock()
    feed.get_departures = AsyncMock(return_value=[])
    app.dependency_overrides[get_stop_departure_feed] = lambda: feed

    response = client.get("/stop-departures", params=params, headers=_CITY_HEADER)

    assert response.status_code == 422
    feed.get_departures.assert_not_awaited()
