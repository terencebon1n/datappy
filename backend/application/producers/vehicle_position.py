from backend.application.ports import MessageProducer, VehiclePositionSource
from backend.application.producers.registry import ProducerTask
from backend.domain.gtfs_rt.vehicle_position import VehiclePosition


class VehiclePositionIngestorService:
    def __init__(
        self, client: VehiclePositionSource, producer: MessageProducer
    ) -> None:
        self.client = client
        self.producer = producer

    async def run(self, task: ProducerTask) -> None:
        raw_data = await self.client.fetch_rt(task.url)
        positions: list[VehiclePosition] = self.client.parse_feed(raw_data)

        for position in positions:
            await self.producer.send(
                topic=task.feed_type.topic(task.city),
                key=position.id,
                value=position.model_dump_json().encode("utf-8"),
            )
