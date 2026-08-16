from collections.abc import AsyncIterator
from typing import Annotated

from fastapi import Depends, HTTPException, Request
from redis import Redis
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession

from backend.api.v1.context import require_city
from backend.application.services.admin.auth import AdminAuthService
from backend.application.services.admin.process_manager import ProcessManagerService
from backend.application.services.api.alert_feed import AlertFeedService
from backend.application.services.api.nearby_stop_loader import NearbyStopLoaderService
from backend.application.services.api.route_geometry_loader import (
    RouteGeometryLoaderService,
)
from backend.application.services.api.route_loader import RouteLoaderService
from backend.application.services.api.stop_departure_feed import StopDepartureFeed
from backend.application.services.api.stop_loader import StopLoaderService
from backend.application.services.api.trip_loader import TripLoaderService
from backend.domain.admin.session import AdminSession
from backend.domain.gtfs_rt.enums import City
from backend.infrastructure.auth.google import GoogleOAuthAdapter
from backend.infrastructure.auth.session import SessionManager
from backend.infrastructure.config import settings
from backend.infrastructure.database.postgres.manager import PostgresDatabaseManager
from backend.infrastructure.database.postgres.repositories.route import RouteRepository
from backend.infrastructure.database.postgres.repositories.shape import ShapeRepository
from backend.infrastructure.database.postgres.repositories.stop import StopRepository
from backend.infrastructure.database.postgres.repositories.stop_time import (
    StopTimeRepository,
)
from backend.infrastructure.database.postgres.repositories.trip import TripRepository
from backend.infrastructure.database.redis.repositories.alert import AlertRepository
from backend.infrastructure.database.redis.repositories.stop_update import (
    StopUpdateRepository,
)
from backend.infrastructure.docker.adapter import DockerProcessAdapter

db_manager = PostgresDatabaseManager(is_async=False)
async_db_manager = PostgresDatabaseManager(is_async=True)
redis_db = Redis(
    host=settings.redis.host, port=settings.redis.port, decode_responses=True
)

google_oauth = GoogleOAuthAdapter(
    client_id=settings.admin.google.client_id,
    client_secret=settings.admin.google.client_secret,
    redirect_uri=settings.admin.google.redirect_uri,
)

session_manager = SessionManager(secret_key=settings.admin.session_secret_key)

auth_service = AdminAuthService(allowed_email=settings.admin.allowed_email)

process_manager = ProcessManagerService(
    adapter=DockerProcessAdapter(
        image=settings.admin.docker_image,
        network=settings.admin.docker_network,
        host=settings.admin.docker_host,
    )
)


def gtfs_engine_for(city: City) -> AsyncEngine:
    # Per-request engine view; must not mutate the shared engine (concurrent
    # requests for different cities would race on the schema map).
    return async_db_manager.async_engine.execution_options(
        schema_translate_map={"gtfs": city}
    )


async def get_gtfs_session(
    city: Annotated[City, Depends(require_city)],
) -> AsyncIterator[AsyncSession]:
    async with AsyncSession(gtfs_engine_for(city)) as session:
        async with session.begin():
            yield session


GtfsSession = Annotated[AsyncSession, Depends(get_gtfs_session)]


def get_route_loader(session: GtfsSession) -> RouteLoaderService:
    return RouteLoaderService(RouteRepository(session))


def get_stop_loader(session: GtfsSession) -> StopLoaderService:
    return StopLoaderService(StopRepository(session))


def get_nearby_stop_loader(session: GtfsSession) -> NearbyStopLoaderService:
    return NearbyStopLoaderService(StopRepository(session))


def get_route_geometry_loader(session: GtfsSession) -> RouteGeometryLoaderService:
    return RouteGeometryLoaderService(
        ShapeRepository(session), StopRepository(session), TripRepository(session)
    )


def get_stop_departure_feed(session: GtfsSession) -> StopDepartureFeed:
    return StopDepartureFeed(
        StopUpdateRepository(redis_db),
        StopTimeRepository(session),
        TripRepository(session),
        StopRepository(session),
    )


def get_trip_loader(session: GtfsSession) -> TripLoaderService:
    return TripLoaderService(TripRepository(session))


def get_alert_feed() -> AlertFeedService:
    return AlertFeedService(AlertRepository(redis_db))


async def require_admin_session(request: Request) -> AdminSession:
    token = request.cookies.get("admin_session")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        return session_manager.decode(token)
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))
