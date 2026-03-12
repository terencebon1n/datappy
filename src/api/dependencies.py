from redis import Redis

from src.infrastructure.database.postgres.manager import PostgresDatabaseManager

db_manager = PostgresDatabaseManager(is_async=False)
async_db_manager = PostgresDatabaseManager(is_async=True)
redis_db = Redis(host="localhost", port=6379, decode_responses=True)
