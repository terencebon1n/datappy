from sqlalchemy.orm import Session

from src.domain.gtfs.calendar_date import CalendarDate
from src.infrastructure.database.postgres.models.calendar_date import (
    CalendarDateModel,
)
from src.infrastructure.database.repository import BaseRepository


class CalendarDateRepository(BaseRepository[CalendarDate, CalendarDateModel]):
    domain = CalendarDate
    model = CalendarDateModel

    def __init__(self, session: Session) -> None:
        super().__init__(session)
