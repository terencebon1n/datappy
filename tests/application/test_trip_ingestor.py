from unittest.mock import AsyncMock, MagicMock

from backend.application.producers.registry import ProducerTask
from backend.application.producers.trip_update import TripIngestorService
from backend.domain.gtfs_rt.enums import City, FeedType
from backend.domain.gtfs_rt.trip import Trip
from backend.domain.gtfs_rt.trip_update import StopTime, TripUpdate


async def test_run_sends_one_message_per_stop_time():
    trip = Trip(id="t1", schedule_relationship=0, route_id="r1", direction_id=1)
    stop_times = [
        StopTime(
            id=f"s{i}",
            arrival_time=100,
            arrival_delay=0,
            departure_time=110,
            departure_delay=0,
            schedule_relationship=0,
        )
        for i in range(2)
    ]
    trip_update = TripUpdate(id="t1", trip=trip, stop_times=stop_times)

    client = MagicMock()
    client.fetch_rt = AsyncMock(return_value=b"raw")
    client.parse_feed = MagicMock(return_value=[trip_update])
    producer = MagicMock()
    producer.send = AsyncMock()

    service = TripIngestorService(client, producer)
    task = ProducerTask(city=City.MONTPELLIER, feed_type=FeedType.TRIP_UPDATE, url="u")

    await service.run(task)

    client.fetch_rt.assert_awaited_once_with("u")
    client.parse_feed.assert_called_once_with(b"raw")
    assert producer.send.await_count == 2
    _, kwargs = producer.send.await_args_list[0]
    assert kwargs["topic"] == "montpellier.TripUpdate"
    assert kwargs["key"] == "r1_1_s0"
    assert isinstance(kwargs["value"], bytes)


async def test_run_no_events_sends_nothing():
    client = MagicMock()
    client.fetch_rt = AsyncMock(return_value=b"")
    client.parse_feed = MagicMock(return_value=[])
    producer = MagicMock()
    producer.send = AsyncMock()

    task = ProducerTask(city=City.NIMES, feed_type=FeedType.TRIP_UPDATE, url="u")
    await TripIngestorService(client, producer).run(task)

    producer.send.assert_not_awaited()
