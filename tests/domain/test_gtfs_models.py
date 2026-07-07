"""Static-GTFS domain models, including the ``mode='before'`` field validators."""

import pytest

from backend.domain.gtfs.agency import Agency
from backend.domain.gtfs.calendar import Calendar
from backend.domain.gtfs.calendar_date import CalendarDate
from backend.domain.gtfs.feed_info import FeedInfo
from backend.domain.gtfs.route import Route
from backend.domain.gtfs.scheduled_departure import ScheduledDeparture
from backend.domain.gtfs.shape import Shape
from backend.domain.gtfs.stop import Stop
from backend.domain.gtfs.stop_time import StopTime
from backend.domain.gtfs.transfer import Transfer
from backend.domain.gtfs.trip import Trip


def test_agency_minimal_and_full():
    agency = Agency(agency_name="TAM", agency_timezone="Europe/Paris")
    assert agency.name == "TAM"
    assert agency.id is None
    full = Agency(
        agency_id="1",
        agency_name="TAM",
        agency_url="http://tam.fr",
        agency_timezone="Europe/Paris",
        agency_email="a@b.c",
    )
    assert full.id == "1"
    assert full.url == "http://tam.fr"


def test_calendar_and_calendar_date():
    cal = Calendar(
        service_id="s1",
        monday=True,
        tuesday=False,
        wednesday=True,
        thursday=False,
        friday=True,
        saturday=False,
        sunday=False,
        start_date="20260101",
        end_date="20261231",
    )
    assert cal.monday is True and cal.sunday is False
    cd = CalendarDate(service_id="s1", date="20260101", exception_type=1)
    assert cd.exception_type == 1


def test_feed_info():
    info = FeedInfo(
        feed_publisher_name="pub",
        feed_publisher_url="http://x",
        feed_version="1.0",
    )
    assert info.version == "1.0"
    assert info.default_lang is None


def test_route_and_scheduled_departure():
    route = Route(
        route_id="r1",
        route_short_name="1",
        route_long_name="Line 1",
        route_type=0,
    )
    assert route.id == "r1"
    assert route.continuous_drop_off is None
    dep = ScheduledDeparture(
        trip_id="t1", departure_time="08:00:00", arrival_time="08:00:00"
    )
    assert dep.trip_id == "t1"


def test_shape_and_stop():
    shape = Shape(
        shape_id="sh1", shape_pt_lat=43.6, shape_pt_lon=3.9, shape_pt_sequence=1
    )
    assert shape.distance_traveled is None
    stop = Stop(
        stop_id="st1",
        stop_name="Gare",
        stop_lat=43.6,
        stop_lon=3.9,
        parent_station=None,
    )
    assert stop.name == "Gare"


@pytest.mark.parametrize(
    "raw, expected",
    [("12.5", 12.5), ("", 0), (3.2, 3.2)],  # str-with-value, empty-str, passthrough
)
def test_stop_time_shape_dist_validator(raw, expected):
    st = StopTime(
        trip_id="t",
        arrival_time="08:00:00",
        departure_time="08:00:00",
        stop_id="s",
        stop_sequence=1,
        shape_dist_traveled=raw,
    )
    assert st.shape_dist_traveled == expected


@pytest.mark.parametrize("raw, expected", [("2", 2), ("", 0), (1, 1)])
def test_stop_time_timepoint_validator(raw, expected):
    st = StopTime(
        trip_id="t",
        arrival_time="08:00:00",
        departure_time="08:00:00",
        stop_id="s",
        stop_sequence=1,
        timepoint=raw,
    )
    assert st.timepoint == expected


@pytest.mark.parametrize("raw, expected", [("120", 120), ("", 0), (60, 60)])
def test_transfer_min_transfer_time_validator(raw, expected):
    tr = Transfer(
        from_stop_id="a",
        to_stop_id="b",
        transfer_type=2,
        min_transfer_time=raw,
    )
    assert tr.min_transfer_time == expected


@pytest.mark.parametrize("raw, expected", [("1", 1), ("", 0), (2, 2)])
def test_trip_accessibility_validator(raw, expected):
    trip = Trip(
        route_id="r",
        service_id="s",
        trip_id="t",
        wheelchair_accessible=raw,
        bikes_allowed=raw,
        cars_allowed=raw,
    )
    assert trip.wheelchair_accessible == expected
    assert trip.bikes_allowed == expected
    assert trip.cars_allowed == expected
    assert trip.direction_id == 0
