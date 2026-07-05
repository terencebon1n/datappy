from typing import Tuple

from sqlalchemy import Index, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from src.infrastructure.database.postgres.base import GTFSModelBase


class CalendarDateModel(GTFSModelBase):
    __tablename__ = "calendar_date"

    service_id: Mapped[str] = mapped_column(String, primary_key=True)
    date: Mapped[str] = mapped_column(String, primary_key=True)
    exception_type: Mapped[int] = mapped_column(Integer)

    __table_args__: Tuple = (
        Index("idx_calendar_date_date_btree", "date", postgresql_using="btree"),
    )
