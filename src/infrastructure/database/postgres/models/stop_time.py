from typing import Optional, Tuple

from sqlalchemy import Float, ForeignKey, Index, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from src.infrastructure.database.postgres.base import GTFSModelBase
from src.infrastructure.database.postgres.models.stop import StopModel
from src.infrastructure.database.postgres.models.trip import TripModel


class StopTimeModel(GTFSModelBase):
    __tablename__ = "stop_time"

    trip_id: Mapped[str] = mapped_column(
        String, ForeignKey(TripModel.id), primary_key=True
    )
    arrival_time: Mapped[str] = mapped_column(String)
    departure_time: Mapped[str] = mapped_column(String)
    stop_id: Mapped[str] = mapped_column(
        String, ForeignKey(StopModel.id)
    )
    stop_sequence: Mapped[int] = mapped_column(Integer, primary_key=True)
    stop_headsign: Mapped[Optional[str]] = mapped_column(String)
    pickup_type: Mapped[int] = mapped_column(Integer)
    drop_off_type: Mapped[int] = mapped_column(Integer)
    continuous_pickup: Mapped[Optional[int]] = mapped_column(Integer)
    continuous_drop_off: Mapped[Optional[int]] = mapped_column(Integer)
    shape_dist_traveled: Mapped[Optional[float]] = mapped_column(Float)
    timepoint: Mapped[Optional[int]] = mapped_column(Integer)
    pickup_booking_rule_id: Mapped[Optional[str]] = mapped_column(String)
    drop_off_booking_rule_id: Mapped[Optional[str]] = mapped_column(String)

    __table_args__: Tuple = (
        Index("idx_stop_time_trip_id_btree", "trip_id", postgresql_using="btree"),
        Index("idx_stop_time_stop_id_btree", "stop_id", postgresql_using="btree"),
        Index(
            "idx_stop_time_composite_pkey_sequence_btree",
            "trip_id",
            "stop_id",
            "stop_sequence",
            postgresql_using="btree",
        ),
    )
