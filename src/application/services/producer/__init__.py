import asyncio
import logging

from src.application.producers.registry import ProducerRegistry
from src.application.producers.trip_update import TripIngestorService
from src.domain.gtfs_rt.enums import City, FeedType
from src.infrastructure.external.rt.trip_update import TripUpdateGateway
from src.infrastructure.messaging.kafka_admin import KafkaAdminTool
from src.infrastructure.messaging.kafka_producer import KafkaProducerAdapter

logger = logging.getLogger(__name__)

_INITIAL_RETRY_DELAY = 30
_MAX_RETRY_DELAY = 1800


class ProducerService:
    async def start(self, city: City) -> None:
        kafka = KafkaProducerAdapter()
        admin = KafkaAdminTool()
        gateway = TripUpdateGateway()
        service = TripIngestorService(gateway, kafka)

        await admin.ensure_topics([f.value for f in FeedType])

        await kafka.start()

        retry_delay = _INITIAL_RETRY_DELAY

        while True:
            try:
                tasks = ProducerRegistry.get_tasks(city=city, feed=FeedType.TRIP_UPDATE)

                for task in tasks:
                    await service.run(task)

                await asyncio.sleep(10)
                retry_delay = _INITIAL_RETRY_DELAY
            except KeyboardInterrupt:
                break
            except Exception as e:
                logger.error(f"Producer cycle failed: {e} — retrying in {retry_delay}s")
                await asyncio.sleep(retry_delay)
                if retry_delay >= _MAX_RETRY_DELAY:
                    logger.critical("Max retry delay reached, giving up.")
                    raise
                retry_delay = min(retry_delay * 2, _MAX_RETRY_DELAY)

        await kafka.stop()
