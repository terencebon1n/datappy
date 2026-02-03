import asyncio
import logging

from sqlalchemy.orm import Session

from ..dto.gtfs_rt.alert import Alert, AlertContainer, AlertEventProducer
from ..dto.gtfs_rt.update import (
    StopUpdateStream,
    TripUpdate,
    TripUpdateContainer,
    TripUpdateEventProducer,
)
from ..dto.gtfs_rt.vehicle import Vehicle, VehicleContainer, VehicleEventProducer
from ..enums.url import TAM_MMM_GTFS_RT
from src.domain.gtfs.enums import GTFSCityUrls
from src.application.services.gtfs_loader import GTFSLoaderService
from .extract_gtfs import extract_gtfs

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s:\t  %(message)s",
)

logger = logging.getLogger(__name__)


class Init:
    def load_gtfs(self, session: Session) -> None:
        extract_gtfs(TAM_MMM_GTFS_RT.GTFS_ZIP, session)

    def load_gtfs_v2(self, session: Session) -> None:
        gtfs_loader = GTFSLoaderService(session)
        gtfs_loader.perform_import(GTFSCityUrls.MONTPELLIER)

    async def gtfs_rt_producer(self) -> None:
        try:
            run_state = 1
            trip_update_kafka_producer = TripUpdateEventProducer()
            await trip_update_kafka_producer.start()
            await trip_update_kafka_producer.create_topic()
            vehicle_kafka_producer = VehicleEventProducer()
            await vehicle_kafka_producer.start()
            await vehicle_kafka_producer.create_topic()
            alert_kafka_producer = AlertEventProducer()
            await alert_kafka_producer.start()
            await alert_kafka_producer.create_topic()

            while True:
                trip_update_container = TripUpdateContainer()
                trip_update_list: list[
                    TripUpdate
                ] = await trip_update_container.extract(TAM_MMM_GTFS_RT.TRIP_UPDATE)
                for trip_update in trip_update_list:
                    await trip_update_kafka_producer.send_dataclass(trip_update)

                vehicle_container = VehicleContainer()
                vehicle_list: list[Vehicle] = await vehicle_container.extract(
                    TAM_MMM_GTFS_RT.VEHICLE_POSITION
                )

                for vehicle in vehicle_list:
                    await vehicle_kafka_producer.send_dataclass(vehicle)

                alert_container = AlertContainer()
                alert_list: list[Alert] = await alert_container.extract(
                    TAM_MMM_GTFS_RT.ALERT
                )

                for alert in alert_list:
                    await alert_kafka_producer.send_dataclass(alert)

                if run_state:
                    run_state = 0
                    logger.info(
                        f"Running {trip_update_container.__class__.__name__} and {vehicle_container.__class__.__name__} and {alert_container.__class__.__name__}"
                    )
                await asyncio.sleep(10)
        except KeyboardInterrupt:
            run_state = 0
            await trip_update_kafka_producer.stop()
            await vehicle_kafka_producer.stop()
            await alert_kafka_producer.stop()

    def gtfs_rt_consumer(self) -> None:
        test_stream = StopUpdateStream("StopUpdateStream")
        query = test_stream.to_redis()
        query.awaitTermination()
