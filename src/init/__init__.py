from sqlalchemy.orm import Session

from ..dto.gtfs_rt.alert import Alert, AlertContainer, AlertEventProducer
from ..dto.gtfs_rt.update import (
    TripUpdateContainer,
    TripUpdate,
    TripUpdateEventProducer,
)
from ..dto.gtfs_rt.vehicle import Vehicle, VehicleContainer, VehicleEventProducer
from ..enums.url import TAM_MMM_GTFS_RT
from .extract_gtfs import extract_gtfs


class Init:
    def load_gtfs(self, session: Session) -> None:
        extract_gtfs(TAM_MMM_GTFS_RT.GTFS_ZIP, session)

    async def load_gtfs_rt(self) -> None:
        trip_update_container = TripUpdateContainer()
        trip_update_list: list[TripUpdate] = await trip_update_container.extract(
            TAM_MMM_GTFS_RT.TRIP_UPDATE
        )

        async with TripUpdateEventProducer() as trip_update_kafka_producer:
            for trip_update in trip_update_list:
                await trip_update_kafka_producer.send_dataclass(trip_update)

        vehicle_container = VehicleContainer()
        vehicle_list: list[Vehicle] = await vehicle_container.extract(
            TAM_MMM_GTFS_RT.VEHICLE_POSITION
        )

        async with VehicleEventProducer() as vehicle_kafka_producer:
            for vehicle in vehicle_list:
                await vehicle_kafka_producer.send_dataclass(vehicle)

        alert_container = AlertContainer()
        alert_list: list[Alert] = await alert_container.extract(TAM_MMM_GTFS_RT.ALERT)

        async with AlertEventProducer() as alert_kafka_producer:
            for alert in alert_list:
                await alert_kafka_producer.send_dataclass(alert)
