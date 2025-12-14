from __future__ import annotations

import csv
from dataclasses import dataclass
from typing import Optional

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from ..gtfs_base import GTFSContainerBase, GTFSModelBase


@dataclass(frozen=True)
class Agency:
    id: str
    name: str
    url: Optional[str]
    timezone: str
    lang: str
    phone: Optional[str]
    fare_url: Optional[str]

    @classmethod
    def from_model(cls, model: AgencyModel) -> Agency:
        return cls(
            id=model.id,
            name=model.name,
            url=model.url,
            timezone=model.timezone,
            lang=model.lang,
            phone=model.phone,
            fare_url=model.fare_url,
        )

    def to_model(self) -> AgencyModel:
        return AgencyModel.from_dataclass(self)


class AgencyModel(GTFSModelBase[Agency]):
    __tablename__ = "agency"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[str] = mapped_column(String)
    url: Mapped[Optional[str]] = mapped_column(String)
    timezone: Mapped[str] = mapped_column(String)
    lang: Mapped[str] = mapped_column(String)
    phone: Mapped[Optional[str]] = mapped_column(String)
    fare_url: Mapped[Optional[str]] = mapped_column(String)

    @classmethod
    def from_dataclass(cls, agency: Agency) -> AgencyModel:
        return cls(
            id=agency.id,
            name=agency.name,
            url=agency.url,
            timezone=agency.timezone,
            lang=agency.lang,
            phone=agency.phone,
            fare_url=agency.fare_url,
        )


class AgencyContainer(GTFSContainerBase[Agency, AgencyModel]):
    items: list[Agency]

    def __init__(self) -> None:
        super().__init__()

    def extract(self, file_data: csv.DictReader[str]) -> None:
        for data in file_data:
            agency = Agency(
                id=data["agency_id"],
                name=data["agency_name"],
                url=data["agency_url"],
                timezone=data["agency_timezone"],
                lang=data["agency_lang"],
                phone=data["agency_phone"],
                fare_url=data["agency_fare_url"],
            )

            self.items.append(agency)
