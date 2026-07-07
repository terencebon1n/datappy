"""Importing the ORM models executes their declarative table definitions."""

from backend.infrastructure.database.postgres.base import GTFSModelBase
from backend.infrastructure.database.postgres.models.agency import AgencyModel
from backend.infrastructure.database.postgres.models.calendar import CalendarModel
from backend.infrastructure.database.postgres.models.calendar_date import (
    CalendarDateModel,
)
from backend.infrastructure.database.postgres.models.feed_info import FeedInfoModel
from backend.infrastructure.database.postgres.models.route import RouteModel
from backend.infrastructure.database.postgres.models.shape import ShapeModel
from backend.infrastructure.database.postgres.models.stop import StopModel
from backend.infrastructure.database.postgres.models.stop_time import StopTimeModel
from backend.infrastructure.database.postgres.models.transfer import TransferModel
from backend.infrastructure.database.postgres.models.trip import TripModel


def test_models_register_expected_tables():
    tables = {
        AgencyModel: "agency",
        CalendarModel: "calendar",
        CalendarDateModel: "calendar_date",
        FeedInfoModel: "feed_info",
        RouteModel: "route",
        ShapeModel: "shape",
        StopModel: "stop",
        StopTimeModel: "stop_time",
        TransferModel: "transfer",
        TripModel: "trip",
    }
    for model, name in tables.items():
        assert model.__tablename__ == name
        assert issubclass(model, GTFSModelBase)


def test_metadata_schema_is_gtfs():
    assert GTFSModelBase.metadata.schema == "gtfs"
    assert "gtfs.agency" in GTFSModelBase.metadata.tables
