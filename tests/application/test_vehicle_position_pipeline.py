"""Vehicle position producer ingestor, Quix stream definition and API feed."""

from unittest.mock import AsyncMock, MagicMock

from backend.application.dto.vehicle_position import VehiclePathDTO, VehiclePositionDTO
from backend.application.producers.registry import ProducerTask
from backend.application.producers.vehicle_position import (
    VehiclePositionIngestorService,
)
from backend.application.services.api.vehicle_position_feed import VehiclePositionFeed
from backend.domain.gtfs_rt.enums import City, FeedType
from backend.domain.gtfs_rt.trip import Trip
from backend.domain.gtfs_rt.vehicle_position import Position, VehiclePosition

_TASK = ProducerTask(
    city=City.MONTPELLIER, feed_type=FeedType.VEHICLE_POSITION, url="http://feed"
)


def _position(vehicle_id: str = "v1", latitude: float = 43.6) -> VehiclePosition:
    return VehiclePosition(
        id=vehicle_id,
        trip=Trip(id="t1", schedule_relationship=0, route_id="r1", direction_id=0),
        position=Position(latitude=latitude, longitude=3.87, bearing=90, speed=12),
        current_status="IN_TRANSIT_TO",
        timestamp=1700000000,
    )


async def test_ingestor_publishes_every_position_keyed_by_vehicle_id():
    client = MagicMock()
    client.fetch_rt = AsyncMock(return_value=b"raw")
    client.parse_feed = MagicMock(return_value=[_position("v1"), _position("v2")])
    producer = MagicMock()
    producer.send = AsyncMock()

    await VehiclePositionIngestorService(client, producer).run(_TASK)

    client.fetch_rt.assert_awaited_once_with("http://feed")
    assert producer.send.await_count == 2
    topics = {call.kwargs["topic"] for call in producer.send.await_args_list}
    keys = {call.kwargs["key"] for call in producer.send.await_args_list}
    assert topics == {"montpellier.VehiclePosition"}
    assert keys == {"v1", "v2"}


async def test_ingestor_publishes_nothing_for_an_empty_feed():
    client = MagicMock()
    client.fetch_rt = AsyncMock(return_value=b"")
    client.parse_feed = MagicMock(return_value=[])
    producer = MagicMock()
    producer.send = AsyncMock()

    await VehiclePositionIngestorService(client, producer).run(_TASK)

    producer.send.assert_not_awaited()


async def test_feed_returns_positions_sorted_by_vehicle_id():
    repo = MagicMock()
    repo.get_vehicle_positions = AsyncMock(
        return_value=[_position("v2"), _position("v1")]
    )
    feed = VehiclePositionFeed(repo)

    result = await feed.get_positions(VehiclePathDTO(city=City.NIMES, route_id="r1"))

    assert [position.id for position in result] == ["v1", "v2"]
    repo.get_vehicle_positions.assert_awaited_once_with(City.NIMES, "r1")


async def test_feed_handles_no_positions():
    repo = MagicMock()
    repo.get_vehicle_positions = AsyncMock(return_value=[])

    result = await VehiclePositionFeed(repo).get_positions(
        VehiclePathDTO(city=City.NIMES, route_id="r1")
    )

    assert result == []


def test_dto_flattens_the_domain_position():
    dto = VehiclePositionDTO.from_domain(_position("v9", latitude=43.61))

    assert dto.id == "v9"
    assert dto.trip_id == "t1"
    assert dto.route_id == "r1"
    assert dto.direction_id == 0
    assert dto.latitude == 43.61
    assert dto.longitude == 3.87
    assert dto.bearing == 90
    assert dto.speed == 12
    assert dto.current_status == "IN_TRANSIT_TO"
    assert dto.timestamp == 1700000000
