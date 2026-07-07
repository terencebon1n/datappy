"""QuixStreamsStopUpdateStream — the streaming pipeline definition.

A fake StreamingDataFrame executes the ``apply`` lambdas with a sample record
so every column-mapping expression is exercised.
"""

from unittest.mock import MagicMock

from backend.application.consumers.quixstreams.stop_update import (
    QuixStreamsStopUpdateStream,
)
from backend.domain.gtfs_rt.enums import City

_RECORD = {
    "trip": {"id": "t1", "route_id": "r1", "direction_id": 0},
    "stop_time": {
        "id": "s1",
        "departure_time": 111,
        "departure_delay": 1,
        "arrival_time": 110,
        "arrival_delay": 0,
    },
    # top-level keys the group_id lambda reads back
    "route_id": "r1",
    "direction_id": 0,
    "stop_id": "s1",
    "trip_id": "t1",
}


class _FakeSDF:
    """Minimal StreamingDataFrame that actually runs the applied functions."""

    def __init__(self, record: dict) -> None:
        self.record = record
        self.assignments: dict = {}
        self.sunk = None

    def apply(self, fn, metadata: bool = False):  # noqa: ANN001
        if metadata:
            return fn(self.record, b"key", 123, [])
        return fn(self.record)

    def __setitem__(self, key, value) -> None:  # noqa: ANN001
        self.assignments[key] = value

    def __getitem__(self, key):  # noqa: ANN001
        return self

    def group_by(self, key):  # noqa: ANN001
        return self

    def sink(self, sink) -> None:  # noqa: ANN001
        self.sunk = sink


def _adapter_with_sdf(sdf: _FakeSDF) -> MagicMock:
    adapter = MagicMock()
    adapter.stream.return_value = sdf
    return adapter


def test_process_dataframe_maps_columns_and_sinks():
    sdf = _FakeSDF(_RECORD)
    adapter = _adapter_with_sdf(sdf)
    sink = MagicMock()

    stream = QuixStreamsStopUpdateStream(adapter, City.MONTPELLIER, sink)
    stream._process_dataframe()

    adapter.stream.assert_called_once_with("montpellier.TripUpdate")
    # applied lambdas populated the derived columns
    assert sdf.assignments["trip_id"] == "t1"
    assert sdf.assignments["route_id"] == "r1"
    assert sdf.assignments["group_id"] == "montpellier|r1|0|s1|t1"
    assert sdf.assignments["timestamp"] == 123  # metadata lambda
    assert sdf.assignments["departure_time"] == 111
    assert sdf.sunk is sink


def test_context_manager_runs_and_stops_app():
    sdf = _FakeSDF(_RECORD)
    adapter = _adapter_with_sdf(sdf)

    with QuixStreamsStopUpdateStream(adapter, City.NIMES, MagicMock()) as stream:
        stream.run()

    adapter.app.run.assert_called_once()
    adapter.app.stop.assert_called_once()
