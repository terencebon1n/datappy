from __future__ import annotations

import csv
from dataclasses import dataclass

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from ..gtfs_base import GTFSContainerBase, GTFSModelBase
from ..stop import StopModel
from ..trip import TripModel


@dataclass(frozen=True)
class StopTime:
    trip_id: str
    arrival_time: str
    departure_time: str
    stop_id: str
    stop_sequence: int
    pickup_type: int
    drop_off_type: int

    @classmethod
    def from_model(cls, model: StopTimeModel) -> StopTime:
        return cls(
            trip_id=model.trip_id,
            arrival_time=model.arrival_time,
            departure_time=model.departure_time,
            stop_id=model.stop_id,
            stop_sequence=model.stop_sequence,
            pickup_type=model.pickup_type,
            drop_off_type=model.drop_off_type,
        )

    def to_model(self) -> StopTimeModel:
        return StopTimeModel.from_dataclass(self)


class StopTimeModel(GTFSModelBase[StopTime]):
    __tablename__ = "stop_time"

    trip_id: Mapped[str] = mapped_column(
        String, ForeignKey(TripModel.id), primary_key=True
    )
    arrival_time: Mapped[str] = mapped_column(String)
    departure_time: Mapped[str] = mapped_column(String)
    stop_id: Mapped[str] = mapped_column(
        String, ForeignKey(StopModel.id), primary_key=True
    )
    stop_sequence: Mapped[int] = mapped_column(Integer)
    pickup_type: Mapped[int] = mapped_column(Integer)
    drop_off_type: Mapped[int] = mapped_column(Integer)

    @classmethod
    def from_dataclass(cls, stop_time: StopTime) -> StopTimeModel:
        return cls(
            trip_id=stop_time.trip_id,
            arrival_time=stop_time.arrival_time,
            departure_time=stop_time.departure_time,
            stop_id=stop_time.stop_id,
            stop_sequence=stop_time.stop_sequence,
            pickup_type=stop_time.pickup_type,
            drop_off_type=stop_time.drop_off_type,
        )


class StopTimeContainer(GTFSContainerBase[StopTime, StopTimeModel]):
    items: list[StopTime]

    def __init__(self) -> None:
        super().__init__()

    def extract(self, file_data: csv.DictReader[str]) -> None:
        for data in file_data:
            stop_time = StopTime(
                trip_id=data["trip_id"],
                arrival_time=data["arrival_time"],
                departure_time=data["departure_time"],
                stop_id=data["stop_id"],
                stop_sequence=int(data["stop_sequence"]),
                pickup_type=int(data["pickup_type"]),
                drop_off_type=int(data["drop_off_type"]),
            )

            self.items.append(stop_time)
