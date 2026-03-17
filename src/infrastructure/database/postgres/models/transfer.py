from typing import Optional

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from src.infrastructure.database.postgres.base import GTFSModelBase
from src.infrastructure.database.postgres.models.route import RouteModel
from src.infrastructure.database.postgres.models.stop import StopModel
from src.infrastructure.database.postgres.models.trip import TripModel


class TransferModel(GTFSModelBase):
    __tablename__ = "transfer"

    from_stop_id: Mapped[str] = mapped_column(
        String, ForeignKey(StopModel.id), primary_key=True
    )
    to_stop_id: Mapped[str] = mapped_column(
        String, ForeignKey(StopModel.id), primary_key=True
    )
    from_route_id: Mapped[Optional[str]] = mapped_column(
        String, ForeignKey(RouteModel.id)
    )
    to_route_id: Mapped[Optional[str]] = mapped_column(
        String, ForeignKey(RouteModel.id)
    )
    from_trip_id: Mapped[Optional[str]] = mapped_column(
        String, ForeignKey(TripModel.id)
    )
    to_trip_id: Mapped[Optional[str]] = mapped_column(String, ForeignKey(TripModel.id))
    transfer_type: Mapped[int] = mapped_column(Integer)
    min_transfer_time: Mapped[int] = mapped_column(Integer)
