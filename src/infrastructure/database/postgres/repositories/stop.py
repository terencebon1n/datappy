from sqlalchemy.orm import Session

from src.domain.gtfs.stop import Stop
from src.infrastructure.database.postgres.models.stop import StopModel
from src.infrastructure.database.repository import BaseRepository


class StopRepository(BaseRepository[Stop, StopModel]):
    domain = Stop
    model = StopModel

    def __init__(self, session: Session) -> None:
        super().__init__(session)
