from aiokafka import AIOKafkaProducer


class KafkaProducerAdapter:
    def __init__(self, brokers: str):
        self.producer = AIOKafkaProducer(bootstrap_servers=brokers)

    async def start(self):
        await self.producer.start()

    async def stop(self):
        await self.producer.stop()

    async def send(self, topic: str, key: str, value: bytes):
        await self.producer.send_and_wait(
            topic=topic, key=key.encode("utf-8"), value=value
        )
