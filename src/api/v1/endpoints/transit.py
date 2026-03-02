import asyncio
from typing import Annotated, Optional

from fastapi import Query, WebSocket, WebSocketDisconnect

from src.api.dependencies import async_db_manager, redis_db
from src.application.dto.route import ConveyanceDTO, RouteIdDTO, RouteTypeDTO
from src.application.dto.stop import StopNameDTO, TransitPathDTO
from src.application.dto.trip import DirectionDTO, PathDTO
from src.application.services.route_loader import RouteLoaderService
from src.application.services.stop_loader import StopLoaderService
from src.application.services.stop_update_feed import StopUpdateFeed
from src.application.services.trip_loader import TripLoaderService
from src.domain.gtfs_rt.stop_update import StopUpdate

from ..router import gtfs_router


@gtfs_router.get("/route-type", response_model=list[RouteTypeDTO])
async def get_route_types() -> list[RouteTypeDTO]:
    return await RouteLoaderService(async_db_manager.async_session).get_route_types()


@gtfs_router.get("/conveyance", response_model=list[ConveyanceDTO])
async def get_conveyances(
    selection: Annotated[RouteTypeDTO, Query()],
) -> list[ConveyanceDTO]:
    return await RouteLoaderService(async_db_manager.async_session).get_conveyances(
        selection.id
    )


@gtfs_router.get("/stop", response_model=list[StopNameDTO])
async def get_stops(
    selection: Annotated[RouteIdDTO, Query()],
) -> list[StopNameDTO]:
    return await StopLoaderService(async_db_manager.async_session).get_stop_names(
        selection.route_id
    )


@gtfs_router.get("/direction", response_model=DirectionDTO)
async def get_direction(
    selection: Annotated[PathDTO, Query()],
) -> DirectionDTO:
    return await TripLoaderService(async_db_manager.async_session).get_direction(
        selection
    )


@gtfs_router.websocket("/stop-updates")
async def ws_stop_updates(
    websocket: WebSocket, selection: Annotated[TransitPathDTO, Query()]
) -> None:
    await websocket.accept()
    last_data: Optional[list[StopUpdate]] = None
    try:
        while True:
            data: list[StopUpdate] = await StopUpdateFeed(redis_db).get_updates(
                selection
            )
            if data != last_data:
                await websocket.send_json(
                    [stop_update.model_dump() for stop_update in data]
                )
                last_data = data

            await asyncio.sleep(5)

    except WebSocketDisconnect:
        await websocket.close()
        print("Client disconnected")
