from backend.application.dto.trip import DirectionDTO, PathDTO
from backend.application.ports import DirectionReader


class TripLoaderService:
    def __init__(self, trip_repository: DirectionReader) -> None:
        self.trip_repository = trip_repository

    async def get_direction(self, selection: PathDTO) -> DirectionDTO:
        direction: dict = await self.trip_repository.get_direction(
            route_id=selection.route_id,
            origin_name=selection.stop_name__origin,
            destination_name=selection.stop_name__destination,
        )
        return DirectionDTO(**direction)
