"""QuixStreamsAlertStream — the alert streaming pipeline definition."""

from unittest.mock import MagicMock

from backend.application.consumers.quixstreams.alert import QuixStreamsAlertStream
from backend.domain.gtfs_rt.enums import City

_RECORD = {"id": "a1", "header_text": "Header"}


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


def test_process_dataframe_maps_columns_and_sinks():
    sdf = _FakeSDF(_RECORD)
    adapter = _adapter_with_sdf(sdf)
    sink = MagicMock()

    stream = QuixStreamsAlertStream(adapter, City.MONTPELLIER, sink)
    stream._process_dataframe()

    adapter.stream.assert_called_once_with("montpellier.Alert")
    assert sdf.assignments["alert_id"] == "a1"
    assert "header_text" in sdf.selected
    assert sdf.sunk is sink


def test_context_manager_runs_and_stops_app():
    sdf = _FakeSDF(_RECORD)
    adapter = _adapter_with_sdf(sdf)

    with QuixStreamsAlertStream(adapter, City.NIMES, MagicMock()) as stream:
        stream.run()

    adapter.app.run.assert_called_once()
    adapter.app.stop.assert_called_once()
