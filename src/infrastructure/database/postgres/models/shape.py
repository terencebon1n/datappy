from typing import Optional

from sqlalchemy import Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from src.infrastructure.database.postgres.base import GTFSModelBase


class ShapeModel(GTFSModelBase):
    __tablename__ = "shape"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    latitude: Mapped[float] = mapped_column(Float)
    longitude: Mapped[float] = mapped_column(Float)
    sequence: Mapped[int] = mapped_column(Integer, primary_key=True)
    distance_traveled: Mapped[Optional[float]] = mapped_column(Float)
