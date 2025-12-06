import asyncio

import requests
from fastapi import APIRouter, WebSocket
from google.transit import gtfs_realtime_pb2
from sqlalchemy import select, distinct

from ..dto.vehicle import Position, Trip, Vehicle
from ..dto.route import RouteModel
from .websocket import ConnectionManager

gtfs_router = APIRouter()

manager = ConnectionManager()


@gtfs_router.get("/")
async def root() -> dict[str, str]:
    return {"message": "Hello Yes"}


@gtfs_router.get("/route-type")
async def route_type() -> dict[str, str]:
    query = select(distinct(RouteModel.type))
    # need a method to handle session asynchronously


@gtfs_router.websocket("/vehicle-position")
async def vehicle_position(websocket: WebSocket) -> None:
    await manager.connect(websocket)
    feed = gtfs_realtime_pb2.FeedMessage()
    url = "https://data.montpellier3m.fr/TAM_MMM_GTFSRT/VehiclePosition.pb"
    while True:
        response = requests.get(url)
        feed.ParseFromString(response.content)
        vehicle_list: list[Vehicle] = []
        for entity in feed.entity:
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

        await websocket.send_json({"yup": f"{vehicle_list[0]}"})
        await asyncio.sleep(5)


@gtfs_router.get("/alert")
async def alert() -> dict[str, str]:
    feed = gtfs_realtime_pb2.FeedMessage()
    url = "https://data.montpellier3m.fr/TAM_MMM_GTFSRT/Alert.pb"
    response = requests.get(url)
    feed.ParseFromString(response.content)
    for entity in feed.entity:
        print(entity)
    return {"message": "Alert"}


@gtfs_router.get("/trip-update")
async def trip_update() -> dict[str, str]:
    feed = gtfs_realtime_pb2.FeedMessage()
    url = "https://data.montpellier3m.fr/TAM_MMM_GTFSRT/TripUpdate.pb"
    response = requests.get(url)
    feed.ParseFromString(response.content)
    for entity in feed.entity:
        print(entity)
    return {"message": "Trip Update"}


@gtfs_router.get("/test")
async def test() -> dict[str, str]:
    return {"message": "test test"}
