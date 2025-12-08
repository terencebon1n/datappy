import asyncio
import time

import requests
from fastapi import APIRouter, WebSocket
from google.transit import gtfs_realtime_pb2
from sqlalchemy import distinct, select

from ..dto.route import RouteModel
from ..dto.stop import StopModel
from ..dto.stop_time import StopTimeModel
from ..dto.trip import TripModel
from ..dto.vehicle import Position, Trip, Vehicle
from ..enums.route_type import RouteType
from .dependencies import async_db_manager
from .websocket import ConnectionManager

gtfs_router = APIRouter()

manager = ConnectionManager()


@gtfs_router.get("/")
async def root() -> dict[str, str]:
    return {"message": "Hello Yes"}


@gtfs_router.get("/route-type")
async def route_type() -> list[str]:
    query = select(distinct(RouteModel.type))
    results = await async_db_manager.async_session.execute(query)

    return [RouteType(route_type).name for route_type in results.scalars().all()]


@gtfs_router.get("/conveyance/{route_type}")
async def conveyange(route_type: str):
    t0 = time.perf_counter()

    query = select(RouteModel.id, RouteModel.short_name, RouteModel.long_name).where(
        RouteModel.type == RouteType[route_type.upper()].value
    )
    results = await async_db_manager.async_session.execute(query)

    t1 = time.perf_counter()

    elapsed = t1 - t0
    return [
        {
            "id": conveyance.id,
            "short_name": conveyance.short_name,
            "long_name": conveyance.long_name,
            "time": elapsed * 1000,
        }
        for conveyance in results.all()
    ]


@gtfs_router.get("/stop/{route_type}/{conveyance}")
async def get_stops(route_type: str, conveyance: str):
    query = (
        select(distinct(StopModel.name))
        .join(StopTimeModel, StopModel.id == StopTimeModel.stop_id, isouter=True)
        .join(TripModel, StopTimeModel.trip_id == TripModel.id, isouter=True)
        .join(RouteModel, TripModel.route_id == RouteModel.id, isouter=True)
        .where(
            RouteModel.type == RouteType[route_type.upper()].value,
            RouteModel.short_name == conveyance,
        )
        .order_by(StopModel.name)
    )

    results = await async_db_manager.async_session.execute(query)

    return [stop for stop in results.scalars().all()]


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
