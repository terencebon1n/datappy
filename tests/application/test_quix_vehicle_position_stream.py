"""QuixStreamsVehiclePositionStream — the vehicle position pipeline definition."""

from unittest.mock import MagicMock

from backend.application.consumers.quixstreams.vehicle_position import (
    QuixStreamsVehiclePositionStream,
)
from backend.domain.gtfs_rt.enums import City

_RECORD = {
    "id": "v1",
    "trip": {
        "id": "t1",
        "route_id": "r1",
        "direction_id": 0,
        "schedule_relationship": 0,
    },
    "position": {
        "latitude": 43.6,
        "longitude": 3.87,
        "bearing": 90,
        "speed": 12,
    },
    "current_status": "IN_TRANSIT_TO",
    "timestamp": 1700000000,
}


class _FakeSDF:
    def __init__(self, record: dict) -> None:
        self.record = record
        self.assignments: dict = {}
        self.selected: list | None = None
        self.sunk = None

    def apply(self, fn, metadata: bool = False):  # noqa: ANN001
        return fn(self.record)

    def __setitem__(self, key, value) -> None:  # noqa: ANN001
        self.assignments[key] = value

    def __getitem__(self, key):  # noqa: ANN001
        self.selected = key
        return self

    def sink(self, sink) -> None:  # noqa: ANN001
        self.sunk = sink


def _adapter_with_sdf(sdf: _FakeSDF) -> MagicMock:
    adapter = MagicMock()
    adapter.stream.return_value = sdf
    return adapter


def test_process_dataframe_flattens_trip_and_position_then_sinks():
    sdf = _FakeSDF(_RECORD)
    adapter = _adapter_with_sdf(sdf)
    sink = MagicMock()

    stream = QuixStreamsVehiclePositionStream(adapter, City.MONTPELLIER, sink)
    stream._process_dataframe()

    adapter.stream.assert_called_once_with("montpellier.VehiclePosition")
    assert sdf.assignments["vehicle_id"] == "v1"
    assert sdf.assignments["trip_id"] == "t1"
    assert sdf.assignments["route_id"] == "r1"
    assert sdf.assignments["direction_id"] == 0
    assert sdf.assignments["schedule_relationship"] == 0
    assert sdf.assignments["latitude"] == 43.6
    assert sdf.assignments["longitude"] == 3.87
    assert sdf.assignments["bearing"] == 90
    assert sdf.assignments["speed"] == 12
    assert sdf.sunk is sink


def test_selected_columns_carry_everything_the_sink_needs():
    sdf = _FakeSDF(_RECORD)

    QuixStreamsVehiclePositionStream(
        _adapter_with_sdf(sdf), City.BORDEAUX, MagicMock()
    )._process_dataframe()

    assert set(sdf.selected) == {
        "vehicle_id",
        "trip_id",
        "route_id",
        "direction_id",
        "schedule_relationship",
        "latitude",
        "longitude",
        "bearing",
        "speed",
        "current_status",
        "timestamp",
    }


def test_context_manager_runs_and_stops_app():
    sdf = _FakeSDF(_RECORD)
    adapter = _adapter_with_sdf(sdf)

    with QuixStreamsVehiclePositionStream(adapter, City.NIMES, MagicMock()) as stream:
        stream.run()

    adapter.app.run.assert_called_once()
    adapter.app.stop.assert_called_once()
