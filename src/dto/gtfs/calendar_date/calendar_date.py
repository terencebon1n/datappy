from __future__ import annotations

import csv
from dataclasses import dataclass

from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from ..gtfs_base import GTFSContainerBase, GTFSModelBase


@dataclass(frozen=True)
class CalendarDate:
    service_id: str
    date: str
    exception_type: int

    @classmethod
    def from_model(cls, model: CalendarDateModel) -> CalendarDate:
        return cls(
            service_id=model.service_id,
            date=model.date,
            exception_type=model.exception_type,
        )

    def to_model(self) -> CalendarDateModel:
        return CalendarDateModel.from_dataclass(self)


class CalendarDateModel(GTFSModelBase[CalendarDate]):
    __tablename__ = "calendar_date"

    service_id: Mapped[str] = mapped_column(String, primary_key=True)
    date: Mapped[str] = mapped_column(String, primary_key=True)
    exception_type: Mapped[int] = mapped_column(Integer)

    @classmethod
    def from_dataclass(cls, calendar_date: CalendarDate) -> CalendarDateModel:
        return cls(
            service_id=calendar_date.service_id,
            date=calendar_date.date,
            exception_type=calendar_date.exception_type,
        )


class CalendarDateContainer(GTFSContainerBase[CalendarDate, CalendarDateModel]):
    items: list[CalendarDate]

    def __init__(self) -> None:
        super().__init__()

    def extract(self, file_data: csv.DictReader[str]) -> None:
        for data in file_data:
            calendar_date = CalendarDate(
                service_id=data["service_id"],
                date=data["date"],
                exception_type=int(data["exception_type"]),
            )

            self.items.append(calendar_date)
