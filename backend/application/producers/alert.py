from backend.application.ports import AlertSource, MessageProducer
from backend.application.producers.registry import ProducerTask
from backend.domain.gtfs_rt.alert import Alert


class AlertIngestorService:
    def __init__(self, client: AlertSource, producer: MessageProducer) -> None:
        self.client = client
        self.producer = producer

    async def run(self, task: ProducerTask) -> None:
        raw_data = await self.client.fetch_rt(task.url)
        alerts: list[Alert] = self.client.parse_feed(raw_data)

        for alert in alerts:
            await self.producer.send(
                topic=task.feed_type.topic(task.city),
                key=alert.id,
                value=alert.model_dump_json().encode("utf-8"),
            )
