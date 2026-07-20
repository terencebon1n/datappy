import asyncio
import logging

from backend.application.producers.alert import AlertIngestorService
from backend.application.producers.registry import ProducerRegistry, ProducerTask
from backend.application.producers.trip_update import TripIngestorService
from backend.domain.gtfs_rt.enums import City, FeedType
from backend.infrastructure.external.rt.alert import AlertGateway
from backend.infrastructure.external.rt.trip_update import TripUpdateGateway
from backend.infrastructure.messaging.kafka_admin import KafkaAdminTool
from backend.infrastructure.messaging.kafka_producer import KafkaProducerAdapter

logger = logging.getLogger(__name__)

_INITIAL_RETRY_DELAY = 30
_MAX_RETRY_DELAY = 1800


class ProducerService:
    async def start(self, city: City) -> None:
        kafka = KafkaProducerAdapter()
        admin = KafkaAdminTool()
        trip_service = TripIngestorService(TripUpdateGateway(), kafka)
        alert_service = AlertIngestorService(AlertGateway(), kafka)

        ingestors = {
            FeedType.TRIP_UPDATE: trip_service.run,
            FeedType.ALERT: alert_service.run,
        }

        await admin.ensure_topics([f.topic(city) for f in FeedType])

        await kafka.start()

        retry_delay = _INITIAL_RETRY_DELAY

        while True:
            try:
                for feed_type, ingest in ingestors.items():
                    tasks: list[ProducerTask] = ProducerRegistry.get_tasks(
                        city=city, feed=feed_type
                    )

                    for task in tasks:
                        await ingest(task)

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
