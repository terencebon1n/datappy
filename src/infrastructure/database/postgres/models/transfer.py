from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from src.infrastructure.database.postgres.base import GTFSModelBase
from src.infrastructure.database.postgres.models.stop import StopModel


class TransferModel(GTFSModelBase):
    __tablename__ = "transfer"

    from_stop_id: Mapped[str] = mapped_column(
        String, ForeignKey(StopModel.id), primary_key=True
    )
    to_stop_id: Mapped[str] = mapped_column(
        String, ForeignKey(StopModel.id), primary_key=True
    )
    transfer_type: Mapped[int] = mapped_column(Integer, primary_key=True)
