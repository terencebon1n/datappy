"""Vehicle position Redis sink (write path) and repository (read path)."""

import json
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import backend.infrastructure.database.redis.sink.vehicle_position as sink_module
from backend.domain.gtfs_rt.enums import City
from backend.infrastructure.database.redis.repositories.vehicle_position import (
    VehiclePositionRepository,
)
from backend.infrastructure.database.redis.sink.vehicle_position import (
    RedisHsetVehiclePositionSink,
)


def _record(vehicle_id: str = "v1", route_id: str = "r1") -> dict:
    return {
        "vehicle_id": vehicle_id,
        "trip_id": "t1",
        "route_id": route_id,
        "direction_id": 0,
        "schedule_relationship": 0,
        "latitude": 43.6,
        "longitude": 3.87,
        "bearing": 90,
        "speed": 12,
        "current_status": "IN_TRANSIT_TO",
        "timestamp": 1700000000,
    }


def test_sink_setup_pings_client():
    sink = RedisHsetVehiclePositionSink(City.MONTPELLIER, host="h", port=1)
    with patch.object(sink_module.redis, "Redis") as redis_cls:
        sink.setup()
    redis_cls.assert_called_once()
    redis_cls.return_value.ping.assert_called_once()


def test_sink_writes_one_field_per_vehicle_under_a_route_key():
    sink = RedisHsetVehiclePositionSink(City.MONTPELLIER, host="h", port=1)
    pipe = MagicMock()
    client = MagicMock()
    client.pipeline.return_value.__enter__.return_value = pipe
    sink._client = client

    batch = MagicMock()
    batch.size = 2
    batch.__iter__.return_value = iter(
        [
            SimpleNamespace(value=_record("v1")),
            SimpleNamespace(value=_record("v2")),
        ]
    )

    sink.write(batch)

    keys = {call.args[0] for call in pipe.hset.call_args_list}
    fields = {call.args[1] for call in pipe.hset.call_args_list}
    assert keys == {"montpellier|vehicles|r1"}
    assert fields == {"v1", "v2"}
    pipe.expire.assert_called_with("montpellier|vehicles|r1", 120)
    pipe.execute.assert_called_once_with(raise_on_error=True)


def test_sink_separates_routes():
    sink = RedisHsetVehiclePositionSink(City.NIMES, host="h", port=1)
    pipe = MagicMock()
    client = MagicMock()
    client.pipeline.return_value.__enter__.return_value = pipe
    sink._client = client

    batch = MagicMock()
    batch.size = 2
    batch.__iter__.return_value = iter(
        [
            SimpleNamespace(value=_record("v1", route_id="r1")),
            SimpleNamespace(value=_record("v2", route_id="r2")),
        ]
    )

    sink.write(batch)

    assert {call.args[0] for call in pipe.hset.call_args_list} == {
        "nimes|vehicles|r1",
        "nimes|vehicles|r2",
    }


async def test_repository_reads_and_rebuilds_domain_positions():
    redis = MagicMock()
    redis.hgetall.return_value = {"v1": json.dumps(_record("v1"))}

    positions = await VehiclePositionRepository(redis).get_vehicle_positions(
        City.MONTPELLIER, "r1"
    )

    redis.hgetall.assert_called_once_with("montpellier|vehicles|r1")
    assert positions[0].id == "v1"
    assert positions[0].trip.route_id == "r1"
    assert positions[0].position.latitude == 43.6
    assert positions[0].position.bearing == 90
    assert positions[0].current_status == "IN_TRANSIT_TO"


async def test_repository_returns_empty_when_the_key_is_missing():
    redis = MagicMock()
    redis.hgetall.return_value = {}

    assert (
        await VehiclePositionRepository(redis).get_vehicle_positions(City.NIMES, "r1")
        == []
    )


async def test_repository_skips_malformed_entries_but_keeps_the_rest():
    redis = MagicMock()
    redis.hgetall.return_value = {
        "bad-json": "{not json",
        "missing-field": json.dumps({"vehicle_id": "v2"}),
        "wrong-type": json.dumps({**_record("v3"), "latitude": "north"}),
        "good": json.dumps(_record("v4")),
    }

    positions = await VehiclePositionRepository(redis).get_vehicle_positions(
        City.MONTPELLIER, "r1"
    )

    assert [position.id for position in positions] == ["v4"]
