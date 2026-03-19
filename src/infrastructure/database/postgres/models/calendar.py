from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column

from src.infrastructure.database.postgres.base import GTFSModelBase


class CalendarModel(GTFSModelBase):
    __tablename__ = "calendar"

    service_id: Mapped[str] = mapped_column(String, primary_key=True)
    monday: Mapped[bool] = mapped_column(Boolean)
    tuesday: Mapped[bool] = mapped_column(Boolean)
    wednesday: Mapped[bool] = mapped_column(Boolean)
    thursday: Mapped[bool] = mapped_column(Boolean)
    friday: Mapped[bool] = mapped_column(Boolean)
    saturday: Mapped[bool] = mapped_column(Boolean)
    sunday: Mapped[bool] = mapped_column(Boolean)
    start_date: Mapped[str] = mapped_column(String)
    end_date: Mapped[str] = mapped_column(String)
