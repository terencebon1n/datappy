from ..database import DatabaseManager
from ..init import Init

db_manager = DatabaseManager(is_async=False)
async_db_manager = DatabaseManager(is_async=True)
init = Init()
