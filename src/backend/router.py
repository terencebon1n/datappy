import asyncio
from datetime import date
from time import time

import requests
from fastapi import APIRouter, WebSocket
from google.transit import gtfs_realtime_pb2
from sqlalchemy import and_, distinct, select
from sqlalchemy.orm import aliased

from ..dto.calendar_date import CalendarDateModel
from ..dto.route import RouteModel
from ..dto.stop import StopModel
from ..dto.stop_time import StopTimeModel
from ..dto.trip import TripModel
from ..dto.update import TripUpdate
from ..dto.update.stop_time import StopTime
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


@gtfs_router.get("/trip-updates-rt/{conveyance}/{direction}/{stop_id}")
async def get_trip_updates_rt(conveyance: str, direction: str, stop_id: str):

    feed = gtfs_realtime_pb2.FeedMessage()
    url = "https://data.montpellier3m.fr/TAM_MMM_GTFSRT/TripUpdate.pb"
    response = requests.get(url)
    feed.ParseFromString(response.content)

    trip_update_list: list[TripUpdate] = []
    for entity in feed.entity:
        stop_time_list: list[StopTime] = []
        if (
            str(entity.trip_update.trip.route_id) == conveyance
            and str(entity.trip_update.trip.direction_id) == direction
        ):
            for stop_time in entity.trip_update.stop_time_update:
                if (
                    stop_time.departure.time > int(time())
                    and stop_time.stop_id == stop_id
                ):
                    stop_time_list.append(
                        StopTime(
                            stop_id=stop_time.stop_id,
                            arrival_delay=stop_time.arrival.delay,
                            arrival_time=stop_time.arrival.time,
                            departure_delay=stop_time.departure.delay,
                            departure_time=stop_time.departure.time,
                            schedule_relationship=stop_time.schedule_relationship,
                        )
                    )
            if stop_time_list:
                trip_update_list.append(
                    TripUpdate(
                        id=entity.id,
                        trip=Trip(
                            id=entity.trip_update.trip.trip_id,
                            schedule_relationship=entity.trip_update.trip.schedule_relationship,
                            route_id=entity.trip_update.trip.route_id,
                            direction_id=entity.trip_update.trip.direction_id,
                        ),
                        stop_times=stop_time_list,
                    )
                )

    return trip_update_list


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
