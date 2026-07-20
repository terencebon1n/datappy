from unittest.mock import AsyncMock, MagicMock

from backend.api.dependencies import (
    get_alert_feed,
    get_route_loader,
    get_stop_loader,
    get_trip_loader,
)
from backend.application.dto.route import ConveyanceDTO
from backend.application.dto.stop import StopNameDTO
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
