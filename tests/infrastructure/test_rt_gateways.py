"""Protobuf GTFS-RT parsers, fed with real serialized FeedMessage payloads."""

from unittest.mock import AsyncMock, MagicMock, patch

from google.transit import gtfs_realtime_pb2 as pb

import backend.infrastructure.external.rt.trip_update as tu_module
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
