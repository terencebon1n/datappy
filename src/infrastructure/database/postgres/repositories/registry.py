from collections.abc import KeysView
from typing import Dict, Type

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from src.domain.gtfs.enums import GTFSFileNames
from src.infrastructure.database.repository import BaseRepository

from .agency import AgencyRepository
from .calendar import CalendarRepository
from .calendar_date import CalendarDateRepository
from .route import RouteRepository
from .shape import ShapeRepository
from .stop import StopRepository
from .stop_time import StopTimeRepository
from .transfer import TransferRepository
from .trip import TripRepository


class RepositoryRegistry:
    _mapping: Dict[GTFSFileNames, Type[BaseRepository]] = {
        GTFSFileNames.AGENCY: AgencyRepository,
        GTFSFileNames.CALENDAR: CalendarRepository,
        GTFSFileNames.CALENDAR_DATES: CalendarDateRepository,
        GTFSFileNames.ROUTES: RouteRepository,
        GTFSFileNames.STOPS: StopRepository,
        GTFSFileNames.TRANSFERS: TransferRepository,
        GTFSFileNames.TRIPS: TripRepository,
        GTFSFileNames.SHAPES: ShapeRepository,
        GTFSFileNames.STOP_TIMES: StopTimeRepository,
    }

    @classmethod
    def get_repository_for_file(
        cls, file_type: GTFSFileNames, session: Session | AsyncSession
    ) -> BaseRepository:
        repository_class = cls._mapping.get(file_type)

        if not repository_class:
            raise ValueError(f"No repository registered for {file_type.name}")

        return repository_class(session)

    @classmethod
    def supported_files(cls) -> KeysView[GTFSFileNames]:
        return cls._mapping.keys()
