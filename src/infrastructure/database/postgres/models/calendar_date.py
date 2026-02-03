from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from src.infrastructure.database.postgres.base import GTFSModelBase


class CalendarDateModel(GTFSModelBase):
    __tablename__ = "calendar_date"

    service_id: Mapped[str] = mapped_column(String, primary_key=True)
    date: Mapped[str] = mapped_column(String, primary_key=True)
    exception_type: Mapped[int] = mapped_column(Integer)
