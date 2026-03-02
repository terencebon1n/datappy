from sqlalchemy import Row
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from src.application.dto.trip import DirectionDTO, PathDTO
from src.infrastructure.database.postgres.repositories.trip import TripRepository


class TripLoaderService:
    def __init__(self, session: Session | AsyncSession) -> None:
        self.trip_repository = TripRepository(session)

    async def get_direction(self, selection: PathDTO) -> DirectionDTO:
        direction: dict = await self.trip_repository.get_direction(
            route_id=selection.route_id,
            origin_name=selection.stop_name__origin,
            destination_name=selection.stop_name__destination,
        )
        return DirectionDTO(**direction)
