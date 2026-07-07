from unittest.mock import AsyncMock, MagicMock, patch

import backend.infrastructure.messaging.kafka_admin as admin_module
import backend.infrastructure.messaging.kafka_producer as producer_module
from backend.infrastructure.messaging.kafka_admin import KafkaAdminTool
from backend.infrastructure.messaging.kafka_producer import KafkaProducerAdapter


def _admin_client() -> MagicMock:
    client = MagicMock()
    client.start = AsyncMock()
    client.close = AsyncMock()
    client.create_topics = AsyncMock()
    return client


async def test_ensure_topics_creates_missing_ones():
    client = _admin_client()
    client.list_topics = AsyncMock(return_value=["existing"])

    with patch.object(admin_module, "AIOKafkaAdminClient", return_value=client):
        await KafkaAdminTool().ensure_topics(["existing", "new-topic"])

    client.start.assert_awaited_once()
    client.create_topics.assert_awaited_once()
    created = client.create_topics.call_args.kwargs["new_topics"]
    assert [t.name for t in created] == ["new-topic"]
    client.close.assert_awaited_once()


async def test_ensure_topics_noop_when_all_exist():
    client = _admin_client()
    client.list_topics = AsyncMock(return_value=["a", "b"])

    with patch.object(admin_module, "AIOKafkaAdminClient", return_value=client):
        await KafkaAdminTool().ensure_topics(["a", "b"])

    client.create_topics.assert_not_awaited()
    client.close.assert_awaited_once()


async def test_producer_adapter_delegates():
    producer = MagicMock()
    producer.start = AsyncMock()
    producer.stop = AsyncMock()
    producer.send_and_wait = AsyncMock()

    with patch.object(producer_module, "AIOKafkaProducer", return_value=producer):
        adapter = KafkaProducerAdapter()
        await adapter.start()
        await adapter.send("topic", "key", b"value")
        await adapter.stop()

    producer.start.assert_awaited_once()
    producer.stop.assert_awaited_once()
    producer.send_and_wait.assert_awaited_once_with(
        topic="topic", key=b"key", value=b"value"
    )
