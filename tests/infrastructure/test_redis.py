import json
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

import backend.infrastructure.database.redis.context as ctx_module
import backend.infrastructure.database.redis.sink.stop_update as sink_module
from backend.domain.gtfs_rt.enums import City
from backend.domain.gtfs_rt.stop_update import StopUpdate
from backend.infrastructure.database.redis.context import RedisPipelineContext
from backend.infrastructure.database.redis.repositories.stop_update import (
    StopUpdateRepository,
)
from backend.infrastructure.database.redis.sink.stop_update import (
    RedisHsetStopUpdateSink,
)


def test_pipeline_context_executes_on_clean_exit():
    with patch.object(ctx_module, "Redis") as redis_cls:
        client = redis_cls.return_value
        pipe = client.pipeline.return_value
        with RedisPipelineContext(host="h", port=1) as ctx:
            ctx.add_to_pipeline("k", "f", "v", ttl=100)

    pipe.hset.assert_called_once_with("k", "f", "v")
    pipe.expire.assert_called_once_with("k", 100)
    pipe.execute.assert_called_once()
    client.close.assert_called_once()


def test_pipeline_context_skips_execute_on_error():
    with patch.object(ctx_module, "Redis") as redis_cls:
        client = redis_cls.return_value
        pipe = client.pipeline.return_value
        with pytest.raises(RuntimeError):
            with RedisPipelineContext() as ctx:
                ctx.add_to_pipeline("k", "f", "v")
                raise RuntimeError("boom")

    pipe.execute.assert_not_called()
    client.close.assert_called_once()


async def test_get_stop_updates_empty_returns_empty_list():
    redis = MagicMock()
    redis.hgetall.return_value = {}
    repo = StopUpdateRepository(redis)
    assert await repo.get_stop_updates(City.MONTPELLIER, "r", 0, "s") == []


async def test_get_stop_updates_parses_and_skips_malformed():
    good = StopUpdate(
        trip_id="t1",
        timestamp=1,
        departure_time=2,
        departure_delay=0,
        arrival_time=2,
        arrival_delay=0,
    )
    redis = MagicMock()
    redis.hgetall.return_value = {
        "a": good.model_dump_json(),
        "b": "{ not valid json",  # JSONDecodeError -> skipped
        "c": json.dumps({"trip_id": "x"}),  # schema error -> skipped
    }
    repo = StopUpdateRepository(redis)

    result = await repo.get_stop_updates(City.MONTPELLIER, "r", 0, "s")

    assert len(result) == 1
    assert result[0].trip_id == "t1"


def test_sink_setup_pings_client():
    sink = RedisHsetStopUpdateSink(City.MONTPELLIER, host="h", port=1)
    with patch.object(sink_module.redis, "Redis") as redis_cls:
        sink.setup()
    redis_cls.assert_called_once()
    redis_cls.return_value.ping.assert_called_once()


def test_sink_write_flushes_batch():
    sink = RedisHsetStopUpdateSink(City.MONTPELLIER, host="h", port=1)
    client = MagicMock()
    pipe = client.pipeline.return_value.__enter__.return_value
    sink._client = client

    item = SimpleNamespace(
        value={
            "route_id": "r1",
            "direction_id": 0,
            "stop_id": "s1",
            "trip_id": "t1",
            "departure_time": 1,
        }
    )
    batch = MagicMock()
    batch.size = 1
    batch.__iter__.return_value = iter([item])

    sink.write(batch)

    pipe.hset.assert_called_once()
    args = pipe.hset.call_args.args
    assert args[0] == "montpellier|r1|0|s1"
    assert args[1] == "t1"
    pipe.expire.assert_called_once_with("montpellier|r1|0|s1", 300)
    pipe.execute.assert_called_once_with(raise_on_error=True)
