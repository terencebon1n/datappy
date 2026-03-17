import asyncio

from src.application.producers.registry import ProducerRegistry
from src.application.producers.trip_update import TripIngestorService
from src.domain.gtfs_rt.enums import City, FeedType
from src.infrastructure.external.rt.trip_update import TripUpdateGateway
from src.infrastructure.messaging.kafka_admin import KafkaAdminTool
from src.infrastructure.messaging.kafka_producer import KafkaProducerAdapter


class ProducerService:
    async def start(self, city: City) -> None:
        kafka = KafkaProducerAdapter()
        admin = KafkaAdminTool()
        gateway = TripUpdateGateway()
        service = TripIngestorService(gateway, kafka)

        await admin.ensure_topics([f.value for f in FeedType])

        await kafka.start()

        while True:
            try:
                tasks = ProducerRegistry.get_tasks(
                    city=city, feed=FeedType.TRIP_UPDATE
                )

                for task in tasks:
                    await service.run(task)

                await asyncio.sleep(10)
            except KeyboardInterrupt:
                break

        await kafka.stop()
