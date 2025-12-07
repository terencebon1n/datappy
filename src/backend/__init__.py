from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI

from ..database import DatabaseManager
from ..init import Init
from ..dto.gtfs_base import GTFSModelBase
from .router import gtfs_router

db_manager = DatabaseManager(is_async=False)


async def initialize_database():
    db_manager.initialize()
    GTFSModelBase.metadata.create_all(db_manager.engine)
    await db_manager.close()


async_db_manager = DatabaseManager(is_async=True)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load
    await initialize_database()
    async_db_manager.initialize()
    init = Init()
    init.start()
    yield
    # Clean up
    await async_db_manager.close()


app = FastAPI(lifespan=lifespan)

app.include_router(gtfs_router)


class BackEnd:
    def start(self) -> None:
        uvicorn.run(
            "src.backend.__init__:app",
            host="0.0.0.0",
            port=8000,
            reload=False,
            log_level="info",
        )
