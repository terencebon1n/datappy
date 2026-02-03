from typing import Optional

from sqlalchemy import Integer, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from src.infrastructure.database.postgres.base import GTFSModelBase
from src.infrastructure.database.postgres.models.agency import AgencyModel


class RouteModel(GTFSModelBase):
    __tablename__ = "route"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    agency_id: Mapped[str] = mapped_column(String, ForeignKey(AgencyModel.id))
    short_name: Mapped[str] = mapped_column(String)
    long_name: Mapped[str] = mapped_column(String)
    type: Mapped[int] = mapped_column(Integer)
    color: Mapped[str] = mapped_column(String)
    text_color: Mapped[Optional[str]] = mapped_column(String)
    url: Mapped[Optional[str]] = mapped_column(String)
