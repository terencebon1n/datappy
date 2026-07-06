from typing import Sequence

from backend.application.dto.stop import StopNameDTO
from backend.application.ports import StopNameReader


class StopLoaderService:
    def __init__(self, stop_repository: StopNameReader) -> None:
        self.stop_repository = stop_repository

    async def get_stop_names(self, route_id: str) -> list[StopNameDTO]:
        stops: Sequence[str] = await self.stop_repository.get_stop_names(route_id)
        return [StopNameDTO(name=stop) for stop in stops]
