import asyncio
import time
from typing import Annotated, Awaitable, Callable, Optional

from fastapi import (
    Depends,
    Query,
    WebSocket,
    WebSocketDisconnect,
)
from sqlalchemy.ext.asyncio import AsyncSession

from backend.api.dependencies import (
    get_alert_feed,
    get_nearby_stop_loader,
    get_route_geometry_loader,
    get_route_loader,
    get_stop_loader,
    get_trip_loader,
    gtfs_engine_for,
    redis_db,
)
from backend.application.dto.alert import AlertDTO, AlertPathDTO
from backend.application.dto.geometry import RouteGeometryDTO
from backend.application.dto.route import ConveyanceDTO, RouteIdDTO
from backend.application.dto.stop import (
    NearbyQueryDTO,
    NearbyStopDTO,
    StopNameDTO,
    TransitPathDTO,
)
from backend.application.dto.trip import DirectionDTO, PathDTO
from backend.application.dto.vehicle_position import VehiclePathDTO, VehiclePositionDTO
from backend.application.services.api.alert_feed import AlertFeedService
from backend.application.services.api.nearby_stop_loader import NearbyStopLoaderService
from backend.application.services.api.route_geometry_loader import (
    RouteGeometryLoaderService,
)
from backend.application.services.api.route_loader import RouteLoaderService
from backend.application.services.api.stop_loader import StopLoaderService
from backend.application.services.api.stop_update_feed import StopUpdateFeed
from backend.application.services.api.trip_loader import TripLoaderService
from backend.application.services.api.vehicle_position_feed import VehiclePositionFeed
from backend.domain.gtfs_rt.enums import City
from backend.domain.gtfs_rt.stop_update import StopUpdate
from backend.infrastructure.database.postgres.repositories.stop_time import (
    StopTimeRepository,
)
from backend.infrastructure.database.redis.repositories.stop_update import (
    StopUpdateRepository,
)
from backend.infrastructure.database.redis.repositories.vehicle_position import (
    VehiclePositionRepository,
)

from ..router import basic_router, gtfs_router, gtfs_rt_router

# How often the feed is polled, and the longest the server stays silent before
# re-sending the current payload as a keepalive so idle proxies don't drop the
# connection.
_POLL_INTERVAL_SECONDS = 5
_KEEPALIVE_SECONDS = 25


@basic_router.get("/city")
async def get_cities() -> list[City]:
    return list(City)


@gtfs_router.get("/conveyance", response_model=list[ConveyanceDTO])
async def get_conveyances(
    route_loader: Annotated[RouteLoaderService, Depends(get_route_loader)],
) -> list[ConveyanceDTO]:
    return await route_loader.get_conveyances()


@gtfs_router.get("/stop", response_model=list[StopNameDTO])
async def get_stops(
    selection: Annotated[RouteIdDTO, Query()],
    stop_loader: Annotated[StopLoaderService, Depends(get_stop_loader)],
) -> list[StopNameDTO]:
    return await stop_loader.get_stop_names(selection.route_id)


@gtfs_router.get("/nearby-stops", response_model=list[NearbyStopDTO])
async def get_nearby_stops(
    selection: Annotated[NearbyQueryDTO, Query()],
    nearby_stop_loader: Annotated[
        NearbyStopLoaderService, Depends(get_nearby_stop_loader)
    ],
) -> list[NearbyStopDTO]:
    return await nearby_stop_loader.get_nearby_stops(selection)


@gtfs_router.get("/route-geometry", response_model=RouteGeometryDTO)
async def get_route_geometry(
    selection: Annotated[RouteIdDTO, Query()],
    geometry_loader: Annotated[
        RouteGeometryLoaderService, Depends(get_route_geometry_loader)
    ],
) -> RouteGeometryDTO:
    return await geometry_loader.get_route_geometry(selection.route_id)


@gtfs_router.get("/direction", response_model=DirectionDTO)
async def get_direction(
    selection: Annotated[PathDTO, Query()],
    trip_loader: Annotated[TripLoaderService, Depends(get_trip_loader)],
) -> DirectionDTO:
    return await trip_loader.get_direction(selection)


@gtfs_rt_router.get("/alerts", response_model=list[AlertDTO])
async def get_alerts(
    selection: Annotated[AlertPathDTO, Query()],
    alert_feed: Annotated[AlertFeedService, Depends(get_alert_feed)],
) -> list[AlertDTO]:
    alerts = await alert_feed.get_alerts(selection)
    return [AlertDTO.from_domain(alert) for alert in alerts]


async def _stream_until_disconnect(
    websocket: WebSocket,
    poll: Callable[[], Awaitable[list]],
) -> None:
    async def monitor_connection() -> None:
        try:
            while True:
                await websocket.receive_text()
        except WebSocketDisconnect:
            return

    async def produce() -> None:
        last_payload: Optional[list] = None
        last_sent_at = 0.0
        while True:
            try:
                payload = await poll()
            except Exception:
                # Transient DB/Redis failure: close the socket so the client
                # reconnects rather than hanging on a dead feed.
                return

            now = time.monotonic()
            if payload != last_payload or now - last_sent_at >= _KEEPALIVE_SECONDS:
                await websocket.send_json(payload)
                last_payload = payload
                last_sent_at = now

            await asyncio.sleep(_POLL_INTERVAL_SECONDS)

    tasks = [
        asyncio.create_task(produce()),
        asyncio.create_task(monitor_connection()),
    ]

    _, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)

    for task in pending:
        task.cancel()

        try:
            await task
        except asyncio.CancelledError:
            pass


@gtfs_rt_router.websocket("/stop-updates")
async def ws_stop_updates(
    websocket: WebSocket, selection: Annotated[TransitPathDTO, Query()]
) -> None:
    await websocket.accept()

    stop_update_repository = StopUpdateRepository(redis_db)
    engine = gtfs_engine_for(selection.city)

    async def poll() -> list:
        # A fresh session per poll returns the pooled connection between polls
        # instead of pinning one (and an open transaction) for the whole
        # connection lifetime.
        async with AsyncSession(engine) as session:
            async with session.begin():
                feed = StopUpdateFeed(
                    stop_update_repository,
                    StopTimeRepository(session),
                )
                updates: list[StopUpdate] = await feed.get_updates(selection)
        return [stop_update.model_dump() for stop_update in updates]

    await _stream_until_disconnect(websocket, poll)


@gtfs_rt_router.websocket("/vehicle-positions")
async def ws_vehicle_positions(
    websocket: WebSocket, selection: Annotated[VehiclePathDTO, Query()]
) -> None:
    await websocket.accept()

    feed = VehiclePositionFeed(VehiclePositionRepository(redis_db))

    async def poll() -> list:
        positions = await feed.get_positions(selection)
        return [
            VehiclePositionDTO.from_domain(position).model_dump()
            for position in positions
        ]

    await _stream_until_disconnect(websocket, poll)
