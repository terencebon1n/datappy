from typing import Optional, Tuple

from sqlalchemy import Boolean, ForeignKey, Index, Integer, String
from sqlalchemy.orm import Mapped, foreign, mapped_column, relationship, remote

from src.infrastructure.database.postgres.base import GTFSModelBase
from src.infrastructure.database.postgres.models.calendar_date import CalendarDateModel
from src.infrastructure.database.postgres.models.route import RouteModel


class TripModel(GTFSModelBase):
    __tablename__ = "trip"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    route_id: Mapped[str] = mapped_column(String, ForeignKey(RouteModel.id))
    service_id: Mapped[str] = mapped_column(String)
    headsign: Mapped[str] = mapped_column(String)
    short_name: Mapped[str] = mapped_column(String)
    direction_id: Mapped[int] = mapped_column(Integer)
    wheelchair_accessible: Mapped[Optional[bool]] = mapped_column(Boolean)
    bikes_allowed: Mapped[Optional[bool]] = mapped_column(Boolean)

    service_dates = relationship(
        CalendarDateModel,
        primaryjoin=foreign(service_id) == remote(CalendarDateModel.service_id),
        foreign_keys=[service_id],
        remote_side=[CalendarDateModel.service_id],
        viewonly=True,
    )

    __table_args__: Tuple = (
        Index("idx_trip_route_id_btree", "route_id", postgresql_using="btree"),
        Index(
            "idx_trip_pkey_route_id_btree", "id", "route_id", postgresql_using="btree"
        ),
    )
