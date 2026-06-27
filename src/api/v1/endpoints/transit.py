import asyncio
import time
from typing import Annotated, Optional

from fastapi import (
    Query,
    WebSocket,
    WebSocketDisconnect,
)
from sqlalchemy.ext.asyncio import AsyncSession

from src.api import async_db_manager
from src.api.dependencies import redis_db
from src.application.dto.route import ConveyanceDTO, RouteIdDTO
from src.application.dto.stop import StopNameDTO, TransitPathDTO
from src.application.dto.trip import DirectionDTO, PathDTO
from src.application.services.api.route_loader import RouteLoaderService
from src.application.services.api.stop_loader import StopLoaderService
from src.application.services.api.stop_update_feed import StopUpdateFeed
from src.application.services.api.trip_loader import TripLoaderService
from src.domain.gtfs_rt.enums import City
from src.domain.gtfs_rt.stop_update import StopUpdate

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
async def get_conveyances() -> list[ConveyanceDTO]:
    async with AsyncSession(async_db_manager.async_engine) as session:
        async with session.begin():
            return await RouteLoaderService(session).get_conveyances()


@gtfs_router.get("/stop", response_model=list[StopNameDTO])
async def get_stops(
    selection: Annotated[RouteIdDTO, Query()],
) -> list[StopNameDTO]:
    async with AsyncSession(async_db_manager.async_engine) as session:
        async with session.begin():
            return await StopLoaderService(session).get_stop_names(selection.route_id)


@gtfs_router.get("/direction", response_model=DirectionDTO)
async def get_direction(
    selection: Annotated[PathDTO, Query()],
) -> DirectionDTO:
    async with AsyncSession(async_db_manager.async_engine) as session:
        async with session.begin():
            return await TripLoaderService(session).get_direction(selection)


@gtfs_rt_router.websocket("/stop-updates")
async def ws_stop_updates(
    websocket: WebSocket, selection: Annotated[TransitPathDTO, Query()]
) -> None:
    await websocket.accept()

    async def monitor_connection() -> None:
        try:
            while True:
                await websocket.receive_text()
        except WebSocketDisconnect:
            return

    async def produce_updates() -> None:
        last_data: Optional[list[StopUpdate]] = None
        last_sent_at = 0.0
        while True:
            # A fresh session per poll returns the pooled connection between
            # polls instead of pinning one (and an open transaction) for the
            # whole connection lifetime.
            try:
                async with AsyncSession(async_db_manager.async_engine) as session:
                    async with session.begin():
                        feed = StopUpdateFeed(redis_db, session)
                        data: list[StopUpdate] = await feed.get_updates(selection)
            except Exception:
                # Transient DB/Redis failure: close the socket so the client
                # reconnects rather than hanging on a dead feed.
                return

            now = time.monotonic()
            if data != last_data or now - last_sent_at >= _KEEPALIVE_SECONDS:
                await websocket.send_json(
                    [stop_update.model_dump() for stop_update in data]
                )
                last_data = data
                last_sent_at = now

            await asyncio.sleep(_POLL_INTERVAL_SECONDS)

    tasks = [
        asyncio.create_task(produce_updates()),
        asyncio.create_task(monitor_connection()),
    ]

    _, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)

    for task in pending:
        task.cancel()

        try:
            await task
        except asyncio.CancelledError:
            pass
