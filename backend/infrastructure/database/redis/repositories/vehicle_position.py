import json
import logging
from typing import List

from redis import Redis

from backend.domain.gtfs_rt.enums import City
from backend.domain.gtfs_rt.trip import Trip
from backend.domain.gtfs_rt.vehicle_position import Position, VehiclePosition

logger = logging.getLogger(__name__)


class VehiclePositionRepository:
    def __init__(self, redis: Redis) -> None:
        self.redis = redis

    async def get_vehicle_positions(
        self, city: City, route_id: str
    ) -> List[VehiclePosition]:
        key = f"{city}|vehicles|{route_id}"

        data = self.redis.hgetall(key)

        if not data:
            return []

        positions = []
        for value in data.values():
            try:
                positions.append(self._to_domain(json.loads(value)))
            except (json.JSONDecodeError, KeyError, ValueError) as e:
                logger.warning(f"Skipping malformed vehicle position in {key}: {e}")
                continue
        return positions

    @staticmethod
    def _to_domain(record: dict) -> VehiclePosition:
        return VehiclePosition(
            id=record["vehicle_id"],
            trip=Trip(
                id=record["trip_id"],
                route_id=record["route_id"],
                direction_id=record["direction_id"],
                schedule_relationship=record["schedule_relationship"],
            ),
            position=Position(
                latitude=record["latitude"],
                longitude=record["longitude"],
                bearing=record["bearing"],
                speed=record["speed"],
            ),
            current_status=record["current_status"],
            timestamp=record["timestamp"],
        )
