from redis import Redis

from src.infrastructure.config import settings
from src.infrastructure.database.postgres.manager import PostgresDatabaseManager

db_manager = PostgresDatabaseManager(is_async=False)
async_db_manager = PostgresDatabaseManager(is_async=True)
redis_db = Redis(
    host=settings.redis.host, port=settings.redis.port, decode_responses=True
)
