from typing import List

from google.transit import gtfs_realtime_pb2

from src.domain.gtfs_rt.trip import Trip
from src.domain.gtfs_rt.vehicle_position import Position, VehiclePosition


class VehiclePositionGateway:
    def parse_feed(self, payload: bytes) -> List[VehiclePosition]:
        feed = gtfs_realtime_pb2.FeedMessage()
        feed.ParseFromString(payload)

        vehicle_positions = []
        for entity in feed.entity:
            if not entity.HasField("vehicle"):
                continue

            vehicle = entity.vehicle
            trip = vehicle.trip
            position = vehicle.position

            vehicle_positions.append(
                VehiclePosition(
                    id=entity.id,
                    trip=Trip(
                        id=trip.trip_id,
                        schedule_relationship=trip.schedule_relationship,
                        route_id=trip.route_id,
                        direction_id=trip.direction_id,
                    ),
                    position=Position(
                        latitude=position.latitude,
                        longitude=position.longitude,
                        bearing=position.bearing,
                        speed=position.speed,
                    ),
                    current_status=vehicle.current_status,
                    timestamp=vehicle.timestamp,
                )
            )
        return vehicle_positions
