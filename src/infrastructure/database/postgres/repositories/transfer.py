from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from src.domain.gtfs.transfer import Transfer
from src.infrastructure.database.postgres.models.transfer import TransferModel
from src.infrastructure.database.repository import BaseRepository


class TransferRepository(BaseRepository[Transfer, TransferModel]):
    domain = Transfer
    model = TransferModel

    def __init__(self, session: Session | AsyncSession) -> None:
        super().__init__(session)
