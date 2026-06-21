from fastapi import HTTPException, Request
from redis import Redis

from src.application.services.admin.auth import AdminAuthService
from src.application.services.admin.process_manager import ProcessManagerService
from src.domain.admin.session import AdminSession
from src.infrastructure.auth.google import GoogleOAuthAdapter
from src.infrastructure.auth.session import SessionManager
from src.infrastructure.config import settings
from src.infrastructure.database.postgres.manager import PostgresDatabaseManager
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


async def require_admin_session(request: Request) -> AdminSession:
    token = request.cookies.get("admin_session")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        return session_manager.decode(token)
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))
