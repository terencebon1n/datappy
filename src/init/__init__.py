from sqlalchemy.orm import Session

from ..dto.gtfs_rt.alert import AlertContainer
from ..dto.gtfs_rt.update import TripUpdateContainer
from ..dto.gtfs_rt.vehicle import VehicleContainer
from ..enums.url import TAM_MMM_GTFS_RT
from .extract_gtfs import extract_gtfs


class Init:
    def load_gtfs(self, session: Session) -> None:
        extract_gtfs(TAM_MMM_GTFS_RT.GTFS_ZIP, session)

    async def load_gtfs_rt(self) -> None:
        trip_update_container = TripUpdateContainer()
        await trip_update_container.extract(TAM_MMM_GTFS_RT.TRIP_UPDATE)

        vehicle_container = VehicleContainer()
        await vehicle_container.extract(TAM_MMM_GTFS_RT.VEHICLE_POSITION)

        alert_container = AlertContainer()
        await alert_container.extract(TAM_MMM_GTFS_RT.ALERT)
