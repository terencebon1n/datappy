from typing import Optional

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from src.infrastructure.database.postgres.base import GTFSModelBase
from src.infrastructure.database.postgres.models.agency import AgencyModel


class RouteModel(GTFSModelBase):
    __tablename__ = "route"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    agency_id: Mapped[str] = mapped_column(String, ForeignKey(AgencyModel.id))
    short_name: Mapped[str] = mapped_column(String)
    long_name: Mapped[str] = mapped_column(String)
    description: Mapped[Optional[str]] = mapped_column(String)
    type: Mapped[int] = mapped_column(Integer)
    url: Mapped[Optional[str]] = mapped_column(String)
    color: Mapped[Optional[str]] = mapped_column(String)
    text_color: Mapped[Optional[str]] = mapped_column(String)
    sort_order: Mapped[Optional[int]] = mapped_column(Integer)
    continuous_pickup: Mapped[Optional[int]] = mapped_column(Integer)
    continuous_drop_off: Mapped[Optional[int]] = mapped_column(Integer)
    network_id: Mapped[Optional[str]] = mapped_column(String)
    cemv_support: Mapped[Optional[str]] = mapped_column(String)
