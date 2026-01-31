import asyncio
import json
from dataclasses import asdict
from datetime import date, datetime, timedelta, timezone
from typing import Optional

import redis
import requests
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from google.transit import gtfs_realtime_pb2
from sqlalchemy import and_, distinct, select
from sqlalchemy.orm import aliased

from ..dto.gtfs import (
    CalendarDateModel,
    RouteModel,
    StopModel,
    StopTimeModel,
    TripModel,
)
from ..dto.gtfs_rt import StopUpdate, Trip, Vehicle
from ..dto.gtfs_rt.vehicle import Position
from ..enums.route_type import RouteType
from .dependencies import async_db_manager
from .websocket import ConnectionManager

gtfs_router = APIRouter()

manager = ConnectionManager()


@gtfs_router.get("/")
async def root() -> dict[str, str]:
    return {"message": "Hello Yes"}


@gtfs_router.get("/route-type")
async def get_route_types() -> list[str]:
    query = select(distinct(RouteModel.type))
    results = await async_db_manager.async_session.execute(query)

    return [RouteType(route_type).name for route_type in results.scalars().all()]


@gtfs_router.get("/conveyance/{route_type}")
async def get_conveyances(route_type: str):
    query = select(RouteModel.id, RouteModel.short_name, RouteModel.long_name).where(
        RouteModel.type == RouteType[route_type.upper()].value
    )
    results = await async_db_manager.async_session.execute(query)

    return [
        {
            "id": conveyance.id,
            "short_name": conveyance.short_name,
            "long_name": conveyance.long_name,
        }
        for conveyance in results.all()
    ]


@gtfs_router.get("/stop/{route_id}")
async def get_stops(route_id: str):
    query = (
        select(distinct(StopModel.name))
        .join(StopTimeModel, StopTimeModel.stop_id == StopModel.id)
        .join(TripModel, StopTimeModel.trip_id == TripModel.id)
        .join(CalendarDateModel, CalendarDateModel.service_id == TripModel.service_id)
        .where(
            and_(
                TripModel.route_id == route_id,
                CalendarDateModel.date == date.today().strftime("%Y%m%d"),
            )
        )
        .order_by(StopModel.name)
    )

    results = await async_db_manager.async_session.execute(query)

    return [stop for stop in results.scalars().all()]


@gtfs_router.get("/direction/{conveyance}/{origin}/{destination}")
async def get_direction(conveyance: str, origin: str, destination: str):
    st_origin = aliased(StopTimeModel, name="st_origin")
    st_destination = aliased(StopTimeModel, name="st_destination")
    s_origin = aliased(StopModel, name="s_origin")
    s_destination = aliased(StopModel, name="s_destination")

    query = (
        select(
            TripModel.direction_id,
            s_origin.id.label("origin_stop_id"),
            s_destination.id.label("destination_stop_id"),
        )
        .select_from(TripModel)
        .join(st_destination, st_destination.trip_id == TripModel.id)
        .join(s_destination, s_destination.id == st_destination.stop_id)
        .join(st_origin, st_origin.trip_id == TripModel.id)
        .join(s_origin, s_origin.id == st_origin.stop_id)
        .where(
            and_(
                TripModel.route_id == conveyance,
                s_destination.name == destination,
                s_origin.name == origin,
                st_destination.stop_sequence > st_origin.stop_sequence,
            )
        )
        .limit(1)
    )

    results = await async_db_manager.async_session.execute(query)

    output = results.all()

    if len(output) == 0:
        return {
            "direction_id": None,
            "origin_stop_id": None,
            "destination_stop_id": None,
        }

    return {
        "direction_id": output[0].direction_id,
        "origin_stop_id": output[0].origin_stop_id,
        "destination_stop_id": output[0].destination_stop_id,
    }


@gtfs_router.get("/vehicles-rt/{conveyance}/{direction}")
async def get_vehicles_rt(conveyance: str, direction: str):
    feed = gtfs_realtime_pb2.FeedMessage()
    url = "https://data.montpellier3m.fr/TAM_MMM_GTFSRT/VehiclePosition.pb"
    response = requests.get(url)
    feed.ParseFromString(response.content)
    vehicle_list: list[Vehicle] = []
    for entity in feed.entity:
        if (
            str(entity.vehicle.trip.route_id) == conveyance
            and str(entity.vehicle.trip.direction_id) == direction
        ):
            vehicle_list.append(
                Vehicle(
                    id=entity.id,
                    trip=Trip(
                        id=entity.vehicle.trip.trip_id,
                        schedule_relationship=entity.vehicle.trip.schedule_relationship,
                        route_id=entity.vehicle.trip.route_id,
                        direction_id=entity.vehicle.trip.direction_id,
                    ),
                    position=Position(
                        latitude=entity.vehicle.position.latitude,
                        longitude=entity.vehicle.position.longitude,
                        bearing=entity.vehicle.position.bearing,
                        speed=entity.vehicle.position.speed,
                    ),
                    current_status=entity.vehicle.current_status,
                    timestamp=entity.vehicle.timestamp,
                )
            )

    return vehicle_list


class TransitRedisReader:
    def __init__(self, host="localhost", port=6379):
        # Decode_responses=True is essential to get strings instead of bytes
        self.r = redis.Redis(host=host, port=port, decode_responses=True)

    async def get_stop_data(self, route_id, direction_id, stop_id) -> list[StopUpdate]:
        """Fetch all trips currently active at a specific stop."""
        key = f"{route_id}:{direction_id}:{stop_id}"

        # FIX: Use hgetall() instead of get()
        # This returns a dict of {trip_id: json_string}
        raw_data = self.r.hgetall(key)

        if not raw_data:
            return []

        # Convert the hash values (JSON strings) into Python objects
        stop_updates: list[StopUpdate] = []

        for value in raw_data.values():
            json_values = json.loads(value)
            timestamp = datetime.strptime(
                json_values["timestamp"], "%Y-%m-%d %H:%M:%S.%f"
            ).replace(tzinfo=timezone.utc)
            stop_update = StopUpdate(
                trip_id=json_values["trip_id"],
                timestamp=json_values["timestamp"],
                departure_time=json_values["departure_time"],
                departure_delay=json_values["departure_delay"],
                arrival_time=json_values["arrival_time"],
                arrival_delay=json_values["arrival_delay"],
            )
            if timestamp < datetime.now(tz=timezone.utc) - timedelta(
                minutes=5
            ) or stop_update.departure_time < int(
                (datetime.now() - timedelta(minutes=1)).timestamp()
            ):
                continue

            stop_updates.append(stop_update)

        stop_updates.sort(key=lambda stop_update: stop_update.departure_time)
        return stop_updates

    async def get_all_stops_for_route(self, route_id):
        """Fetch all stops and their trips for a route."""
        pattern = f"{route_id}:*:*"
        keys = self.r.keys(pattern)

        results = {}
        for key in keys:
            # FIX: Use hgetall() here as well
            data = self.r.hgetall(key)
            if data:
                results[key] = [json.loads(v) for v in data.values()]
        return results


# @gtfs_router.get("/trip-updates-rt/{conveyance}/{direction}/{stop_id}")
# async def get_trip_updates_rt(conveyance: str, direction: str, stop_id: str):
# Tip: In a real app, don't re-instantiate the reader on every request.
# Use a dependency or global client.
#    reader = TransitRedisReader(host="localhost")
#    return await reader.get_stop_data(conveyance, direction, stop_id)


@gtfs_router.websocket("/trip-updates-rt/{conveyance}/{direction}/{stop_id}")
async def websocket_trip_updates(
    websocket: WebSocket, conveyance: str, direction: str, stop_id: str
):
    await websocket.accept()
    # Use 'localhost' if running FastAPI locally, 'redis' if in Docker
    reader = TransitRedisReader(host="localhost")

    last_data: Optional[list[StopUpdate]] = None
    try:
        while True:
            data: list[StopUpdate] = await reader.get_stop_data(
                conveyance, direction, stop_id
            )

            if data != last_data:
                await websocket.send_json([asdict(stop_update) for stop_update in data])
                last_data = data

            # 3. Wait 1 second before checking Redis again
            await asyncio.sleep(1)

    except WebSocketDisconnect:
        print("Client disconnected")
