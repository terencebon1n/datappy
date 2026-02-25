from src.infrastructure.database.postgres.manager import PostgresDatabaseManager

from ..init import Init

db_manager = PostgresDatabaseManager(is_async=False)
async_db_manager = PostgresDatabaseManager(is_async=True)
init = Init()
