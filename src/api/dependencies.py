from collections.abc import AsyncIterator
from typing import Annotated

from fastapi import Depends, HTTPException, Request
from redis import Redis
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession

from src.api.v1.context import require_city
from src.application.services.admin.auth import AdminAuthService
from src.application.services.admin.process_manager import ProcessManagerService
from src.application.services.api.route_loader import RouteLoaderService
from src.application.services.api.stop_loader import StopLoaderService
from src.application.services.api.trip_loader import TripLoaderService
from src.domain.admin.session import AdminSession
from src.domain.gtfs_rt.enums import City
from src.infrastructure.auth.google import GoogleOAuthAdapter
from src.infrastructure.auth.session import SessionManager
from src.infrastructure.config import settings
from src.infrastructure.database.postgres.manager import PostgresDatabaseManager
from src.infrastructure.database.postgres.repositories.route import RouteRepository
from src.infrastructure.database.postgres.repositories.stop import StopRepository
from src.infrastructure.database.postgres.repositories.trip import TripRepository
from src.infrastructure.docker.adapter import DockerProcessAdapter

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


def get_trip_loader(session: GtfsSession) -> TripLoaderService:
    return TripLoaderService(TripRepository(session))


async def require_admin_session(request: Request) -> AdminSession:
    token = request.cookies.get("admin_session")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        return session_manager.decode(token)
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))
