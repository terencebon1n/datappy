from sqlalchemy.orm import Session

from src.domain.gtfs.stop_time import StopTime
from src.infrastructure.database.postgres.models.stop_time import StopTimeModel
from src.infrastructure.database.repository import BaseRepository


class StopTimeRepository(BaseRepository):
    domain = StopTime
    model = StopTimeModel

    def __init__(self, session: Session) -> None:
        super().__init__(session)
