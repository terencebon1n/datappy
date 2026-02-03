from typing import Optional, Tuple

from sqlalchemy import Float, Index, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from src.infrastructure.database.postgres.base import GTFSModelBase


class StopModel(GTFSModelBase):
    __tablename__ = "stop"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    code: Mapped[int] = mapped_column(Integer)
    name: Mapped[str] = mapped_column(String)
    tts_name: Mapped[str] = mapped_column(String)
    latitude: Mapped[float] = mapped_column(Float)
    longitude: Mapped[float] = mapped_column(Float)
    location_type: Mapped[str] = mapped_column(String)
    parent_station: Mapped[Optional[str]] = mapped_column(String)
    wheelchair_boarding: Mapped[int] = mapped_column(Integer)

    __table_args__: Tuple = (
        Index("idx_stop_name_hash", "name", postgresql_using="hash"),
    )
