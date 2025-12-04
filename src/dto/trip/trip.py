from __future__ import annotations

import csv
from dataclasses import dataclass
from typing import Optional

from sqlalchemy import Boolean, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, foreign, mapped_column, relationship, remote

from ..calendar_date import CalendarDateModel
from ..gtfs_base import GTFSContainerBase, GTFSModelBase
from ..route import RouteModel


@dataclass(frozen=True)
class Trip:
    route_id: str
    service_id: str
    id: str
    headsign: str
    short_name: str
    direction_id: int
    wheelchair_accessible: Optional[bool]
    bikes_allowed: Optional[bool]

    @classmethod
    def from_model(cls, model: TripModel) -> Trip:
        return cls(
            route_id=model.route_id,
            service_id=model.service_id,
            id=model.id,
            headsign=model.headsign,
            short_name=model.short_name,
            direction_id=model.direction_id,
            wheelchair_accessible=model.wheelchair_accessible,
            bikes_allowed=model.bikes_allowed,
        )

    def to_model(self) -> TripModel:
        return TripModel.from_dataclass(self)


class TripModel(GTFSModelBase[Trip]):
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
        viewonly=True 
    )

    @classmethod
    def from_dataclass(cls, trip: Trip) -> TripModel:
        return cls(
            id=trip.id,
            route_id=trip.route_id,
            service_id=trip.service_id,
            headsign=trip.headsign,
            short_name=trip.short_name,
            direction_id=trip.direction_id,
            wheelchair_accessible=trip.wheelchair_accessible,
            bikes_allowed=trip.bikes_allowed,
        )


class TripContainer(GTFSContainerBase[Trip, TripModel]):
    items: list[Trip]

    def __init__(self) -> None:
        super().__init__()

    def extract(self, file_data: csv.DictReader[str]) -> None:
        for data in file_data:
            trip = Trip(
                route_id=data["route_id"],
                service_id=data["service_id"],
                id=data["trip_id"],
                headsign=data["trip_headsign"],
                short_name=data["trip_short_name"],
                direction_id=int(data["direction_id"]),
                wheelchair_accessible=bool(data["wheelchair_accessible"]),
                bikes_allowed=bool(data["bikes_allowed"]),
            )

            self.items.append(trip)
