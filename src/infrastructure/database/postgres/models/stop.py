from typing import Optional, Tuple

from sqlalchemy import Float, Index, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from src.infrastructure.database.postgres.base import GTFSModelBase


class StopModel(GTFSModelBase):
    __tablename__ = "stop"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    code: Mapped[Optional[str]] = mapped_column(String)
    name: Mapped[str] = mapped_column(String)
    tts_name: Mapped[Optional[str]] = mapped_column(String)
    description: Mapped[Optional[str]] = mapped_column(String)
    latitude: Mapped[float] = mapped_column(Float)
    longitude: Mapped[float] = mapped_column(Float)
    zone_id: Mapped[Optional[str]] = mapped_column(String)
    url: Mapped[Optional[str]] = mapped_column(String)
    location_type: Mapped[Optional[str]] = mapped_column(String)
    parent_station: Mapped[Optional[str]] = mapped_column(String)
    timezone: Mapped[Optional[str]] = mapped_column(String)
    wheelchair_boarding: Mapped[Optional[int]] = mapped_column(Integer)
    level_id: Mapped[Optional[str]] = mapped_column(String)
    platform_code: Mapped[Optional[str]] = mapped_column(String)

    __table_args__: Tuple = (
        Index("idx_stop_name_hash", "name", postgresql_using="hash"),
    )
