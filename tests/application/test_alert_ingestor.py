"""AlertIngestorService — fetches the alert feed and publishes one message per alert."""

from unittest.mock import AsyncMock, MagicMock

from backend.application.producers.alert import AlertIngestorService
from backend.application.producers.registry import ProducerTask
from backend.domain.gtfs_rt.alert import Alert, InformedEntity
from backend.domain.gtfs_rt.enums import City, FeedType

_TASK = ProducerTask(city=City.NIMES, feed_type=FeedType.ALERT, url="http://feed")


async def test_publishes_each_alert_keyed_by_id():
    alerts = [
        Alert(id="a1", informed_entities=[InformedEntity(route_id="R1")]),
        Alert(id="a2"),
    ]
    client = MagicMock()
    client.fetch_rt = AsyncMock(return_value=b"payload")
    client.parse_feed.return_value = alerts
    producer = MagicMock()
    producer.send = AsyncMock()

    await AlertIngestorService(client, producer).run(_TASK)

    client.fetch_rt.assert_awaited_once_with("http://feed")
    client.parse_feed.assert_called_once_with(b"payload")
    assert producer.send.await_count == 2

    first = producer.send.await_args_list[0].kwargs
    assert first["topic"] == "nimes.Alert"
    assert first["key"] == "a1"
    assert b'"id":"a1"' in first["value"]


async def test_empty_feed_publishes_nothing():
    client = MagicMock()
    client.fetch_rt = AsyncMock(return_value=b"")
    client.parse_feed.return_value = []
    producer = MagicMock()
    producer.send = AsyncMock()

    await AlertIngestorService(client, producer).run(_TASK)

    producer.send.assert_not_awaited()
