from __future__ import annotations

import csv
from dataclasses import dataclass
from typing import Optional

from sqlalchemy import Boolean, Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from ..gtfs_base import GTFSContainerBase, GTFSModelBase


@dataclass(frozen=True)
class Stop:
    id: str
    code: int
    name: str
    tts_name: str
    latitude: float
    longitude: float
    location_type: str
    parent_station: Optional[str]
    wheelchair_boarding: bool

    @classmethod
    def from_model(cls, model: StopModel) -> Stop:
        return cls(
            id=model.id,
            code=model.code,
            name=model.name,
            tts_name=model.tts_name,
            latitude=model.latitude,
            longitude=model.longitude,
            location_type=model.location_type,
            parent_station=model.parent_station,
            wheelchair_boarding=model.wheelchair_boarding,
        )

    def to_model(self) -> StopModel:
        return StopModel.from_dataclass(self)


class StopModel(GTFSModelBase[Stop]):
    __tablename__ = "stop"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    code: Mapped[int] = mapped_column(Integer)
    name: Mapped[str] = mapped_column(String)
    tts_name: Mapped[str] = mapped_column(String)
    latitude: Mapped[float] = mapped_column(Float)
    longitude: Mapped[float] = mapped_column(Float)
    location_type: Mapped[str] = mapped_column(String)
    parent_station: Mapped[Optional[str]] = mapped_column(String)
    wheelchair_boarding: Mapped[bool] = mapped_column(Boolean)

    @classmethod
    def from_dataclass(cls, stop: Stop) -> StopModel:
        return cls(
            id=stop.id,
            code=stop.code,
            name=stop.name,
            tts_name=stop.tts_name,
            latitude=stop.latitude,
            longitude=stop.longitude,
            location_type=stop.location_type,
            parent_station=stop.parent_station,
            wheelchair_boarding=stop.wheelchair_boarding,
        )


class StopContainer(GTFSContainerBase[Stop, StopModel]):
    items: list[Stop]

    def __init__(self) -> None:
        super().__init__()

    def extract(self, file_data: csv.DictReader[str]) -> None:
        for data in file_data:
            stop = Stop(
                id=data["stop_id"],
                code=int(data["stop_code"]),
                name=data["stop_name"],
                tts_name=data["tts_stop_name"],
                latitude=float(data["stop_lat"]),
                longitude=float(data["stop_lon"]),
                location_type=data["location_type"],
                parent_station=data["parent_station"],
                wheelchair_boarding=bool(data["wheelchair_boarding"]),
            )

            self.items.append(stop)
