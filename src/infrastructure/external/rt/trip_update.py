from typing import List

import httpx
from google.transit import gtfs_realtime_pb2

from src.domain.gtfs_rt.trip import Trip
from src.domain.gtfs_rt.trip_update import StopTime, TripUpdate


class TripUpdateGateway:
    async def fetch_rt(self, url: str) -> bytes:
        """Fetch the binary Protobuf from the URL."""
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            response.raise_for_status()  # Raises an error for 4xx/5xx responses
            return response.content

    def _parse_stop_time(self, stop_time_update: list) -> List[StopTime]:
        stop_times = []
        for stop_time in stop_time_update:
            arrival = stop_time.arrival
            departure = stop_time.departure

            stop_times.append(
                StopTime(
                    id=stop_time.stop_id,
                    arrival_delay=arrival.delay,
                    arrival_time=arrival.time,
                    departure_delay=departure.delay,
                    departure_time=departure.time,
                    schedule_relationship=stop_time.schedule_relationship,
                )
            )
        return stop_times

    def parse_feed(self, payload: bytes) -> List[TripUpdate]:
        feed = gtfs_realtime_pb2.FeedMessage()
        feed.ParseFromString(payload)

        trip_updates = []
        for entity in feed.entity:
            if not entity.HasField("trip_update"):
                continue

            trip_update = entity.trip_update
            trip = trip_update.trip

            trip_updates.append(
                TripUpdate(
                    id=entity.id,
                    trip=Trip(
                        id=trip.trip_id,
                        schedule_relationship=trip.schedule_relationship,
                        route_id=trip.route_id,
                        direction_id=trip.direction_id,
                    ),
                    stop_times=self._parse_stop_time(trip_update.stop_time_update),
                )
            )
        return trip_updates
