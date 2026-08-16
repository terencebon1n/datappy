"""Protobuf GTFS-RT parsers, fed with real serialized FeedMessage payloads."""

from unittest.mock import AsyncMock, MagicMock, patch

from google.transit import gtfs_realtime_pb2 as pb

import backend.infrastructure.external.rt.alert as alert_module
import backend.infrastructure.external.rt.trip_update as tu_module
import backend.infrastructure.external.rt.vehicle_position as vp_module
from backend.domain.gtfs_rt.enums import AlertCause, AlertEffect, AlertSeverity
from backend.infrastructure.external.rt.alert import AlertGateway
from backend.infrastructure.external.rt.trip_update import TripUpdateGateway
from backend.infrastructure.external.rt.vehicle_position import VehiclePositionGateway


def _feed() -> pb.FeedMessage:
    feed = pb.FeedMessage()
    feed.header.gtfs_realtime_version = "2.0"
    return feed


def test_trip_update_parse_feed_skips_non_trip_entities():
    feed = _feed()

    entity = feed.entity.add()
    entity.id = "e1"
    entity.trip_update.trip.trip_id = "t1"
    entity.trip_update.trip.route_id = "r1"
    entity.trip_update.trip.direction_id = 1
    stu = entity.trip_update.stop_time_update.add()
    stu.stop_id = "s1"
    stu.arrival.delay = 10
    stu.arrival.time = 100
    stu.departure.delay = 5
    stu.departure.time = 110

    other = feed.entity.add()  # alert entity -> no trip_update -> skipped
    other.id = "e2"
    other.alert.header_text.translation.add().text = "x"

    updates = TripUpdateGateway().parse_feed(feed.SerializeToString())

    assert len(updates) == 1
    assert updates[0].trip.route_id == "r1"
    assert updates[0].stop_times[0].id == "s1"
    assert updates[0].stop_times[0].departure_time == 110


async def test_trip_update_fetch_rt():
    response = MagicMock()
    response.raise_for_status = MagicMock()
    response.content = b"protobuf-bytes"
    client = MagicMock()
    client.get = AsyncMock(return_value=response)
    async_client = MagicMock()
    async_client.__aenter__ = AsyncMock(return_value=client)
    async_client.__aexit__ = AsyncMock(return_value=None)

    with patch.object(tu_module.httpx, "AsyncClient", return_value=async_client):
        data = await TripUpdateGateway().fetch_rt("http://feed")

    assert data == b"protobuf-bytes"
    client.get.assert_awaited_once_with("http://feed")


def test_alert_extract_text_empty():
    assert AlertGateway()._extract_text(pb.TranslatedString()) == ""


def test_alert_parse_feed():
    feed = _feed()

    entity = feed.entity.add()
    entity.id = "a1"
    period = entity.alert.active_period.add()
    period.start = 1
    period.end = 2
    informed = entity.alert.informed_entity.add()
    informed.route_id = "r1"
    informed.stop_id = "s1"
    entity.alert.header_text.translation.add().text = "Header"
    entity.alert.description_text.translation.add().text = "Desc"

    other = feed.entity.add()  # trip_update entity -> not an alert -> skipped
    other.id = "a2"
    other.trip_update.trip.trip_id = "t1"

    alerts = AlertGateway().parse_feed(feed.SerializeToString())

    assert len(alerts) == 1
    assert alerts[0].header_text == "Header"
    assert alerts[0].description_text == "Desc"
    assert alerts[0].active_periods[0].end == 2
    assert alerts[0].informed_entities[0].route_id == "r1"


async def test_alert_fetch_rt_returns_body():
    response = MagicMock()
    response.content = b"alert-bytes"
    client = MagicMock()
    client.get = AsyncMock(return_value=response)
    async_client = MagicMock()
    async_client.__aenter__ = AsyncMock(return_value=client)
    async_client.__aexit__ = AsyncMock(return_value=None)

    with patch.object(alert_module.httpx, "AsyncClient", return_value=async_client):
        data = await AlertGateway().fetch_rt("http://feed")

    assert data == b"alert-bytes"
    client.get.assert_awaited_once_with("http://feed")
    response.raise_for_status.assert_called_once()


def test_alert_parse_feed_maps_enums_and_url():
    feed = _feed()

    entity = feed.entity.add()
    entity.id = "a1"
    entity.alert.cause = pb.Alert.STRIKE
    entity.alert.effect = pb.Alert.NO_SERVICE
    entity.alert.severity_level = pb.Alert.SEVERE
    entity.alert.header_text.translation.add().text = "Header"
    entity.alert.url.translation.add().text = "https://info.fr"
    informed = entity.alert.informed_entity.add()
    informed.route_id = "r1"
    informed.direction_id = 0
    informed.route_type = 3

    alert = AlertGateway().parse_feed(feed.SerializeToString())[0]

    assert alert.cause is AlertCause.STRIKE
    assert alert.effect is AlertEffect.NO_SERVICE
    assert alert.severity is AlertSeverity.SEVERE
    assert alert.url == "https://info.fr"
    # direction_id 0 is a real value, not "unset"
    assert alert.informed_entities[0].direction_id == 0
    assert alert.informed_entities[0].route_type == 3


def test_alert_parse_feed_leaves_unset_selector_fields_none():
    feed = _feed()

    entity = feed.entity.add()
    entity.id = "a1"
    entity.alert.header_text.translation.add().text = "Header"
    entity.alert.informed_entity.add().agency_id = "AG"

    alert = AlertGateway().parse_feed(feed.SerializeToString())[0]
    informed = alert.informed_entities[0]

    assert informed.agency_id == "AG"
    assert informed.route_id is None
    assert informed.stop_id is None
    assert informed.direction_id is None
    assert informed.route_type is None
    assert informed.is_network_wide is True
    # no url translation -> normalised away
    assert alert.url is None


def test_vehicle_position_parse_feed():
    feed = _feed()

    entity = feed.entity.add()
    entity.id = "v1"
    entity.vehicle.trip.trip_id = "t1"
    entity.vehicle.trip.route_id = "r1"
    entity.vehicle.trip.direction_id = 0
    entity.vehicle.position.latitude = 43.6
    entity.vehicle.position.longitude = 3.9
    entity.vehicle.position.bearing = 90
    entity.vehicle.position.speed = 10
    entity.vehicle.current_status = pb.VehiclePosition.IN_TRANSIT_TO
    entity.vehicle.timestamp = 123

    other = feed.entity.add()  # alert entity -> no vehicle -> skipped
    other.id = "v2"
    other.alert.header_text.translation.add().text = "x"

    positions = VehiclePositionGateway().parse_feed(feed.SerializeToString())

    assert len(positions) == 1
    assert positions[0].trip.route_id == "r1"
    assert positions[0].position.bearing == 90
    assert positions[0].current_status == "IN_TRANSIT_TO"
    assert positions[0].timestamp == 123


async def test_vehicle_position_fetch_rt():
    response = MagicMock()
    response.raise_for_status = MagicMock()
    response.content = b"vehicle-bytes"
    client = MagicMock()
    client.get = AsyncMock(return_value=response)
    async_client = MagicMock()
    async_client.__aenter__ = AsyncMock(return_value=client)
    async_client.__aexit__ = AsyncMock(return_value=None)

    with patch.object(vp_module.httpx, "AsyncClient", return_value=async_client):
        data = await VehiclePositionGateway().fetch_rt("http://feed")

    assert data == b"vehicle-bytes"
    client.get.assert_awaited_once_with("http://feed")
    response.raise_for_status.assert_called_once()
