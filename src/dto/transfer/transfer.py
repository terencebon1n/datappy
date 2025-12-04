from __future__ import annotations

import csv
from dataclasses import dataclass

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from ..gtfs_base import GTFSContainerBase, GTFSModelBase
from ..stop import StopModel


@dataclass(frozen=True)
class Transfer:
    from_stop_id: str
    to_stop_id: str
    transfer_type: int

    @classmethod
    def from_model(cls, model: TransferModel) -> Transfer:
        return cls(
            from_stop_id=model.from_stop_id,
            to_stop_id=model.to_stop_id,
            transfer_type=model.transfer_type,
        )

    def to_model(self) -> TransferModel:
        return TransferModel.from_dataclass(self)


class TransferModel(GTFSModelBase[Transfer]):
    __tablename__ = "transfer"

    from_stop_id: Mapped[str] = mapped_column(
        String, ForeignKey(StopModel.id), primary_key=True
    )
    to_stop_id: Mapped[str] = mapped_column(
        String, ForeignKey(StopModel.id), primary_key=True
    )
    transfer_type: Mapped[int] = mapped_column(Integer, primary_key=True)

    @classmethod
    def from_dataclass(cls, transfer: Transfer) -> TransferModel:
        return cls(
            from_stop_id=transfer.from_stop_id,
            to_stop_id=transfer.to_stop_id,
            transfer_type=transfer.transfer_type,
        )


class TransferContainer(GTFSContainerBase[Transfer, TransferModel]):
    items: list[Transfer]

    def __init__(self) -> None:
        super().__init__()

    def extract(self, file_data: csv.DictReader[str]) -> None:
        for data in file_data:
            transfer = Transfer(
                from_stop_id=data["from_stop_id"],
                to_stop_id=data["to_stop_id"],
                transfer_type=int(data["transfer_type"]),
            )

            self.items.append(transfer)
