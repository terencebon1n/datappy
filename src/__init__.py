import asyncio
import logging

from sqlalchemy.orm import Session
from sqlalchemy.schema import CreateSchema

from src.application.consumers.stop_update import StopUpdateStream
from src.application.producers.registry import ProducerRegistry
from src.application.producers.trip_update import TripIngestorService
from src.application.services.gtfs_loader import GTFSLoaderService
from src.domain.gtfs.enums import GTFSCityUrls
from src.domain.gtfs_rt.enums import City, FeedType
from src.infrastructure.database.postgres.base import GTFSModelBase
from src.infrastructure.database.postgres.manager import PostgresDatabaseManager
from src.infrastructure.database.redis.sink.stop_update import StopUpdateSink
from src.infrastructure.external.rt.trip_update import TripUpdateGateway
from src.infrastructure.messaging.kafka_admin import KafkaAdminTool
from src.infrastructure.messaging.kafka_producer import KafkaProducerAdapter
from src.infrastructure.processing.spark.consumer import SparkConsumerAdapter

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s:\t  %(message)s",
)

logger = logging.getLogger(__name__)


class Init:
    async def gtfs_populate(self) -> None:
        db_manager = PostgresDatabaseManager(is_async=False)
        db_manager.initialize()

        GTFSModelBase.metadata.drop_all(db_manager.engine)

        db_manager.session.execute(CreateSchema("gtfs", if_not_exists=True))
        db_manager.session.commit()
        GTFSModelBase.metadata.create_all(db_manager.engine)

        gtfs_loader = GTFSLoaderService(db_manager.session)
        gtfs_loader.perform_import(GTFSCityUrls.MONTPELLIER)

        await db_manager.close()

    async def gtfs_rt_producer(self) -> None:
        kafka = KafkaProducerAdapter()
        admin = KafkaAdminTool()
        gateway = TripUpdateGateway()
        service = TripIngestorService(gateway, kafka)

        await admin.ensure_topics([f.value for f in FeedType])

        await kafka.start()

        while True:
            try:
                tasks = ProducerRegistry.get_tasks(
                    city=City.MONTPELLIER, feed=FeedType.TRIP_UPDATE
                )

                for task in tasks:
                    await service.run(task)

                await asyncio.sleep(10)
            except KeyboardInterrupt:
                break

        await kafka.stop()

    def gtfs_rt_consumer(self) -> None:
        spark = SparkConsumerAdapter("StopUpdateStream")
        sink = StopUpdateSink()
        with StopUpdateStream(spark, sink) as stream:
            stream.awaitTermination()
