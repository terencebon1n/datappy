from aiokafka import AIOKafkaProducer

from src.infrastructure.config import settings


class KafkaProducerAdapter:
    def __init__(self) -> None:
        self.producer = AIOKafkaProducer(bootstrap_servers=settings.kafka.brokers)

    async def start(self) -> None:
        await self.producer.start()

    async def stop(self) -> None:
        await self.producer.stop()

    async def send(self, topic: str, key: str, value: bytes) -> None:
        await self.producer.send_and_wait(
            topic=topic, key=key.encode("utf-8"), value=value
        )
