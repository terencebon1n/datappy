from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from src.domain.gtfs.calendar import Calendar
from src.infrastructure.database.postgres.models.calendar import CalendarModel
from src.infrastructure.database.repository import BaseRepository


class CalendarRepository(BaseRepository[Calendar, CalendarModel]):
    domain = Calendar
    model = CalendarModel

    def __init__(self, session: Session | AsyncSession) -> None:
        super().__init__(session)
