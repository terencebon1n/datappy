from enum import Enum
from ...dto.agency import AgencyModel
from ...dto.calendar_date import CalendarDateModel
from ...dto.route import RouteModel
from ...dto.stop import StopModel
from ...dto.stop_time import StopTimeModel
from ...dto.transfer import TransferModel
from ...dto.trip import TripModel


class GTFSModel(Enum):
    TRANSFER = TransferModel()
    STOP_TIME = StopTimeModel()
    TRIP = TripModel()
    STOP = StopModel()
    ROUTE = RouteModel()
    AGENCY = AgencyModel()
    CALENDAR_DATE = CalendarDateModel()
