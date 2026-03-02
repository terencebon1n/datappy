from typing import Sequence

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from src.application.dto.stop import StopNameDTO
from src.infrastructure.database.postgres.repositories.stop import StopRepository


class StopLoaderService:
    def __init__(self, session: Session | AsyncSession) -> None:
        self.stop_repository = StopRepository(session)

    async def get_stop_names(self, route_id: str) -> list[StopNameDTO]:
        stops: Sequence[str] = await self.stop_repository.get_stop_names(route_id)
        return [StopNameDTO(name=stop) for stop in stops]
