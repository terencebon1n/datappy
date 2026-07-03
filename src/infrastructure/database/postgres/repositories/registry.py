from collections.abc import KeysView
from typing import Dict, Tuple, Type

from pydantic import BaseModel
from sqlalchemy.orm import Session

from src.domain.gtfs.agency import Agency
from src.domain.gtfs.calendar import Calendar
from src.domain.gtfs.calendar_date import CalendarDate
from src.domain.gtfs.enums import GTFSFileNames
from src.domain.gtfs.feed_info import FeedInfo
from src.domain.gtfs.route import Route
from src.domain.gtfs.shape import Shape
from src.domain.gtfs.stop import Stop
from src.domain.gtfs.stop_time import StopTime
from src.domain.gtfs.transfer import Transfer
from src.domain.gtfs.trip import Trip
from src.infrastructure.database.postgres.base import GTFSModelBase
from src.infrastructure.database.postgres.models.agency import AgencyModel
from src.infrastructure.database.postgres.models.calendar import CalendarModel
from src.infrastructure.database.postgres.models.calendar_date import (
    CalendarDateModel,
)
from src.infrastructure.database.postgres.models.feed_info import FeedInfoModel
from src.infrastructure.database.postgres.models.route import RouteModel
from src.infrastructure.database.postgres.models.shape import ShapeModel
from src.infrastructure.database.postgres.models.stop import StopModel
from src.infrastructure.database.postgres.models.stop_time import StopTimeModel
from src.infrastructure.database.postgres.models.transfer import TransferModel
from src.infrastructure.database.postgres.models.trip import TripModel
from src.infrastructure.database.repository import BulkIngestRepository


class RepositoryRegistry:
    _mapping: Dict[GTFSFileNames, Tuple[Type[BaseModel], Type[GTFSModelBase]]] = {
        GTFSFileNames.AGENCY: (Agency, AgencyModel),
        GTFSFileNames.CALENDAR: (Calendar, CalendarModel),
        GTFSFileNames.CALENDAR_DATES: (CalendarDate, CalendarDateModel),
        GTFSFileNames.FEED_INFO: (FeedInfo, FeedInfoModel),
        GTFSFileNames.ROUTES: (Route, RouteModel),
        GTFSFileNames.STOPS: (Stop, StopModel),
        GTFSFileNames.TRANSFERS: (Transfer, TransferModel),
        GTFSFileNames.TRIPS: (Trip, TripModel),
        GTFSFileNames.SHAPES: (Shape, ShapeModel),
        GTFSFileNames.STOP_TIMES: (StopTime, StopTimeModel),
    }

    @classmethod
    def get_repository_for_file(
        cls, file_type: GTFSFileNames, session: Session
    ) -> BulkIngestRepository:
        entry = cls._mapping.get(file_type)

        if not entry:
            raise ValueError(f"No repository registered for {file_type.name}")

        domain, model = entry
        return BulkIngestRepository(session, domain=domain, model=model)

    @classmethod
    def supported_files(cls) -> KeysView[GTFSFileNames]:
        return cls._mapping.keys()
