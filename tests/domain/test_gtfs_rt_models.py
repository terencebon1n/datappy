"""Realtime-GTFS domain models: Alert validator + StopUpdate staleness logic."""

from datetime import datetime, timezone

import pytest

from backend.domain.admin.process import ManagedProcess, ProcessStatus
from backend.domain.admin.session import AdminSession
from backend.domain.gtfs_rt.alert import Alert, InformedEntity, Period
from backend.domain.gtfs_rt.enums import City, FeedType
from backend.domain.gtfs_rt.stop_update import StopUpdate
from backend.domain.gtfs_rt.trip import Trip
from backend.domain.gtfs_rt.trip_update import MinimizedTripUpdate, StopTime, TripUpdate
from backend.domain.gtfs_rt.vehicle_position import Position, VehiclePosition


def test_alert_defaults():
    alert = Alert(id="a1")
    assert alert.active_periods == []
    assert alert.header_text == "No Header"
    assert alert.description_text == "No Description"


def test_alert_with_entities_and_periods():
    alert = Alert(
        id="a1",
        active_periods=[Period(start=1, end=2)],
        informed_entities=[InformedEntity(route_id="r", stop_id="s")],
        header_text="Delay",
        description_text="Line down",
    )
    assert alert.active_periods[0].end == 2
    assert alert.informed_entities[0].route_id == "r"
    assert alert.header_text == "Delay"


@pytest.mark.parametrize("raw", ["", "   ", None])
def test_alert_missing_translation_falls_back(raw):
    alert = Alert(id="a1", header_text=raw, description_text=raw)
    assert alert.header_text == "No Translation"
    assert alert.description_text == "No Translation"


def test_alert_keeps_present_translation():
    alert = Alert(id="a1", header_text="Present")
    assert alert.header_text == "Present"


def test_trip_and_trip_update():
    trip = Trip(id="t1", schedule_relationship=0, route_id="r1", direction_id=1)
    st = StopTime(
        id="s1",
        arrival_time=100,
        arrival_delay=0,
        departure_time=110,
        departure_delay=5,
        schedule_relationship=0,
    )
    tu = TripUpdate(id="t1", trip=trip, stop_times=[st])
    assert tu.stop_times[0].departure_delay == 5
    assert TripUpdate(id="t2", trip=trip).stop_times == []
    minimized = MinimizedTripUpdate(id="t1", trip=trip, stop_time=st)
    assert minimized.stop_time.id == "s1"


def test_vehicle_position():
    trip = Trip(id="t1", schedule_relationship=0, route_id="r1", direction_id=0)
    vp = VehiclePosition(
        id="v1",
        trip=trip,
        position=Position(latitude=43.6, longitude=3.9, bearing=90, speed=10),
        current_status="IN_TRANSIT_TO",
        timestamp=123,
    )
    assert vp.position.bearing == 90
    assert vp.current_status == "IN_TRANSIT_TO"


def _stop_update(timestamp: int, departure_time: int) -> StopUpdate:
    return StopUpdate(
        trip_id="t1",
        timestamp=timestamp,
        departure_time=departure_time,
        departure_delay=0,
        arrival_time=departure_time,
        arrival_delay=0,
    )


def test_parse_timestamp_seconds_and_millis():
    su = _stop_update(0, 0)
    seconds = su._parse_timestamp(1_700_000_000)
    millis = su._parse_timestamp(1_700_000_000_000)
    assert seconds == millis  # millis get divided by 1000
    assert seconds == datetime.fromtimestamp(1_700_000_000, tz=timezone.utc)


def test_parse_timestamp_invalid_raises():
    su = _stop_update(0, 0)
    with pytest.raises(ValueError, match="Invalid timestamp format"):
        su._parse_timestamp("not-a-number")


def test_is_stale_false_when_recent_and_future_departure():
    now = datetime.now(timezone.utc)
    ref_ts = int(now.timestamp())
    su = _stop_update(ref_ts, ref_ts + 3600)
    assert su.is_stale(now) is False


def test_is_stale_true_when_timestamp_old():
    now = datetime.now(timezone.utc)
    old_ts = int(now.timestamp()) - 3600
    su = _stop_update(old_ts, int(now.timestamp()) + 3600)
    assert su.is_stale(now) is True


def test_is_stale_true_when_departure_in_past():
    now = datetime.now(timezone.utc)
    ref_ts = int(now.timestamp())
    su = _stop_update(ref_ts, ref_ts - 3600)
    assert su.is_stale(now) is True


def test_admin_process_and_session():
    proc = ManagedProcess(
        service="producer",
        city=City.MONTPELLIER,
        status=ProcessStatus.RUNNING,
        container_name="datappy-producer-montpellier",
    )
    assert proc.city == City.MONTPELLIER
    assert proc.status == ProcessStatus.RUNNING
    session = AdminSession(email="a@b.c", expires_at=datetime.now(timezone.utc))
    assert session.email == "a@b.c"
    # FeedType reused here to keep the realtime enum exercised alongside models
    assert FeedType.TRIP_UPDATE.topic(City.TOULOUSE) == "toulouse.TripUpdate"
