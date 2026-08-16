from backend.application.dto.vehicle_position import VehiclePathDTO
from backend.application.ports import VehiclePositionReader
from backend.domain.gtfs_rt.vehicle_position import VehiclePosition


class VehiclePositionFeed:
    def __init__(self, vehicle_repository: VehiclePositionReader) -> None:
        self.vehicle_repository = vehicle_repository

    async def get_positions(self, selection: VehiclePathDTO) -> list[VehiclePosition]:
        positions = await self.vehicle_repository.get_vehicle_positions(
            selection.city, selection.route_id
        )
        return sorted(positions, key=lambda position: position.id)
