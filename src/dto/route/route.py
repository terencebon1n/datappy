from __future__ import annotations

import csv
from dataclasses import dataclass
from typing import Optional

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from ..agency import AgencyModel
from ..gtfs_base import GTFSContainerBase, GTFSModelBase


@dataclass(frozen=True)
class Route:
    id: str
    agency_id: str
    short_name: str
    long_name: str
    type: int
    color: str
    text_color: Optional[str]
    url: Optional[str]

    @classmethod
    def from_model(cls, model: RouteModel) -> Route:
        return cls(
            id=model.id,
            agency_id=model.agency_id,
            short_name=model.short_name,
            long_name=model.long_name,
            type=model.type,
            color=model.color,
            text_color=model.text_color,
            url=model.url,
        )

    def to_model(self) -> RouteModel:
        return RouteModel.from_dataclass(self)


class RouteModel(GTFSModelBase[Route]):
    __tablename__ = "route"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    agency_id: Mapped[str] = mapped_column(String, ForeignKey(AgencyModel.id))
    short_name: Mapped[str] = mapped_column(String)
    long_name: Mapped[str] = mapped_column(String)
    type: Mapped[int] = mapped_column(Integer)
    color: Mapped[str] = mapped_column(String)
    text_color: Mapped[Optional[str]] = mapped_column(String)
    url: Mapped[Optional[str]] = mapped_column(String)

    @classmethod
    def from_dataclass(cls, route: Route) -> RouteModel:
        return cls(
            id=route.id,
            agency_id=route.agency_id,
            short_name=route.short_name,
            long_name=route.long_name,
            type=route.type,
            color=route.color,
            text_color=route.text_color,
            url=route.url,
        )


class RouteContainer(GTFSContainerBase[Route, RouteModel]):
    items: list[Route]

    def __init__(self) -> None:
        super().__init__()

    def extract(self, file_data: csv.DictReader[str]) -> None:
        for data in file_data:
            route = Route(
                id=data["route_id"],
                agency_id=data["agency_id"],
                short_name=data["route_short_name"],
                long_name=data["route_long_name"],
                type=int(data["route_type"]),
                color=data["route_color"],
                text_color=data["route_text_color"],
                url=data["route_url"],
            )

            self.items.append(route)
