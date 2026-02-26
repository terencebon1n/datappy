from src import Init
from src.infrastructure.database.postgres.manager import PostgresDatabaseManager

db_manager = PostgresDatabaseManager(is_async=False)
async_db_manager = PostgresDatabaseManager(is_async=True)
init = Init()
