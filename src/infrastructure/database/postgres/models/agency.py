from typing import Optional

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from src.infrastructure.database.postgres.base import GTFSModelBase


class AgencyModel(GTFSModelBase):
    __tablename__ = "agency"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[str] = mapped_column(String)
    url: Mapped[Optional[str]] = mapped_column(String)
    timezone: Mapped[str] = mapped_column(String)
    lang: Mapped[str] = mapped_column(String)
    phone: Mapped[Optional[str]] = mapped_column(String)
    fare_url: Mapped[Optional[str]] = mapped_column(String)
