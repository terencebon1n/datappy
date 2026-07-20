"""Composition-root services that wire infrastructure together.

Their collaborators are patched at the service module namespace so no real
Kafka / Redis / Postgres / Docker / graphviz is required.
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

import backend.application.services.api as api_module
import backend.application.services.consumer as consumer_module
import backend.application.services.diagram as diagram_module
import backend.application.services.populate as populate_module
from backend.domain.gtfs_rt.enums import City


def test_api_service_runs_uvicorn():
    with patch.object(api_module, "uvicorn") as uvicorn_mock:
        api_module.ApiService().start()

    uvicorn_mock.run.assert_called_once()
    args, kwargs = uvicorn_mock.run.call_args
    assert args[0] == "backend.api.__init__:app"
    assert kwargs["host"] == "0.0.0.0"
    assert kwargs["port"] == 8000


def test_diagram_service_builds_diagram():
    patches = {
        name: MagicMock()
        for name in (
            "Diagram",
            "Cluster",
            "Custom",
            "PostgreSQL",
            "Redis",
            "Kafka",
            "FastAPI",
            "Python",
        )
    }
    with patch.multiple(diagram_module, **patches):
        diagram_module.DiagramService().start()

    patches["Diagram"].assert_called_once()
    # both external-source custom icons instantiated
    assert patches["Custom"].call_count == 2


def test_consumer_service_starts_both_streams():
    stream_cls = MagicMock()
    alert_stream_cls = MagicMock()
    with (
        patch.object(consumer_module, "QuixStreamsConsumerAdapter") as adapter_cls,
        patch.object(consumer_module, "RedisHsetStopUpdateSink") as sink_cls,
        patch.object(consumer_module, "RedisHsetAlertSink") as alert_sink_cls,
        patch.object(consumer_module, "QuixStreamsStopUpdateStream", stream_cls),
        patch.object(consumer_module, "QuixStreamsAlertStream", alert_stream_cls),
    ):
        consumer_module.QuixStreamsConsumerService().start(City.MONTPELLIER)

    adapter_cls.assert_called_once_with(consumer_group="stop-update-montpellier")
    sink_cls.assert_called_once()
    alert_sink_cls.assert_called_once()
    # both dataframes registered on the single Quix application
    stream_cls.assert_called_once()
    alert_stream_cls.assert_called_once()
    stream_cls.return_value.__enter__.return_value.run.assert_called_once()
    alert_stream_cls.return_value.__enter__.assert_called_once()
    # both streams released on exit
    stream_cls.return_value.__exit__.assert_called_once()
    alert_stream_cls.return_value.__exit__.assert_called_once()


async def test_populate_service_happy_path():
    db_manager = MagicMock()
    db_manager.close = AsyncMock()

    with (
        patch.object(
            populate_module, "PostgresDatabaseManager", return_value=db_manager
        ),
        patch.object(populate_module, "GTFSModelBase") as model_base,
        patch.object(populate_module, "CreateSchema") as create_schema,
        patch.object(populate_module, "GTFSZipReader") as zip_reader,
        patch.object(populate_module, "GTFSLoaderService") as loader_cls,
    ):
        await populate_module.PopulateService().start(City.MONTPELLIER)

    db_manager.initialize.assert_called_once()
    db_manager.set_schema.assert_called_once_with(City.MONTPELLIER)
    model_base.metadata.drop_all.assert_called_once_with(db_manager.engine)
    model_base.metadata.create_all.assert_called_once_with(db_manager.engine)
    create_schema.assert_called_once()
    zip_reader.assert_called_once()
    loader_cls.return_value.perform_import.assert_called_once()
    db_manager.close.assert_awaited_once()


async def test_populate_service_raises_without_feed_config(monkeypatch):
    monkeypatch.setattr(populate_module.settings, "feeds", {})
    with pytest.raises(ValueError, match="No feed configuration"):
        await populate_module.PopulateService().start(City.MONTPELLIER)
