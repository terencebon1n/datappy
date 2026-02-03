from sqlalchemy.orm import Session

from src.domain.gtfs.trip import Trip
from src.infrastructure.database.postgres.models.trip import TripModel
from src.infrastructure.database.repository import BaseRepository


class TripRepository(BaseRepository[Trip, TripModel]):
    domain = Trip
    model = TripModel

    def __init__(self, session: Session) -> None:
        super().__init__(session)
