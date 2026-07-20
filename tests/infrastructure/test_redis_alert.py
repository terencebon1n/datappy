"""Alert Redis sink (write path) and repository (read path)."""

import json
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import backend.infrastructure.database.redis.sink.alert as sink_module
from backend.domain.gtfs_rt.enums import AlertSeverity, City
from backend.infrastructure.database.redis.repositories.alert import AlertRepository
from backend.infrastructure.database.redis.sink.alert import (
    RedisHsetAlertSink,
    alert_key,
)


def _stored(alert_id: str) -> str:
    return json.dumps(
        {
            "alert_id": alert_id,
            "active_periods": [{"start": 1, "end": 2}],
            "informed_entities": [{"route_id": "R1", "stop_id": None}],
            "cause": "STRIKE",
            "effect": "NO_SERVICE",
            "severity": "SEVERE",
            "header_text": "Header",
            "description_text": "Desc",
            "url": None,
        }
    )


def test_alert_key_is_scoped_per_city():
    assert alert_key(City.NIMES) == "nimes|alerts"


def test_sink_setup_pings_client():
    sink = RedisHsetAlertSink(City.MONTPELLIER, host="h", port=1)
    with patch.object(sink_module.redis, "Redis") as redis_cls:
        sink.setup()
    redis_cls.assert_called_once()
    redis_cls.return_value.ping.assert_called_once()


def test_sink_write_flushes_batch_under_one_key():
    sink = RedisHsetAlertSink(City.MONTPELLIER, host="h", port=1)
    client = MagicMock()
    pipe = client.pipeline.return_value.__enter__.return_value
    sink._client = client

    batch = MagicMock()
    batch.size = 2
    batch.__iter__.return_value = iter(
        [
            SimpleNamespace(value={"alert_id": "a1", "header_text": "H1"}),
            SimpleNamespace(value={"alert_id": "a2", "header_text": "H2"}),
        ]
    )

    sink.write(batch)

    assert pipe.hset.call_count == 2
    assert pipe.hset.call_args_list[0].args[0] == "montpellier|alerts"
    assert pipe.hset.call_args_list[0].args[1] == "a1"
    pipe.expire.assert_called_once_with("montpellier|alerts", 3600)
    pipe.execute.assert_called_once_with(raise_on_error=True)


async def test_get_alerts_empty_returns_empty_list():
    redis = MagicMock()
    redis.hgetall.return_value = {}
    assert await AlertRepository(redis).get_alerts(City.MONTPELLIER) == []


async def test_get_alerts_rehydrates_domain_model():
    redis = MagicMock()
    redis.hgetall.return_value = {"a1": _stored("a1")}

    alerts = await AlertRepository(redis).get_alerts(City.MONTPELLIER)

    assert len(alerts) == 1
    assert alerts[0].id == "a1"
    assert alerts[0].severity is AlertSeverity.SEVERE
    assert alerts[0].informed_entities[0].route_id == "R1"
    redis.hgetall.assert_called_once_with("montpellier|alerts")


async def test_get_alerts_skips_malformed_entries():
    redis = MagicMock()
    redis.hgetall.return_value = {
        "a1": _stored("a1"),
        "bad-json": "{ not valid json",
        "no-id": json.dumps({"header_text": "orphan"}),
        "bad-schema": json.dumps({"alert_id": "x", "active_periods": "nope"}),
    }

    alerts = await AlertRepository(redis).get_alerts(City.MONTPELLIER)

    assert [alert.id for alert in alerts] == ["a1"]
