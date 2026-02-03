from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.schema import CreateSchema

from .dependencies import async_db_manager, db_manager, init
from .router import gtfs_router

from src.infrastructure.database.postgres.base import GTFSModelBase


async def initialize_database():
    db_manager.initialize()
    db_manager.session.execute(CreateSchema("gtfs", if_not_exists=True))
    db_manager.session.commit()
    GTFSModelBase.metadata.create_all(db_manager.engine)
    init.load_gtfs(db_manager.session)
    await db_manager.close()


async def drop_database():
    db_manager.initialize()
    GTFSModelBase.metadata.drop_all(db_manager.engine)
    await db_manager.close()


async def initialize_database_v2():
    db_manager.initialize()
    db_manager.session.execute(CreateSchema("gtfs", if_not_exists=True))
    db_manager.session.commit()
    GTFSModelBase.metadata.create_all(db_manager.engine)
    init.load_gtfs_v2(db_manager.session)
    await db_manager.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load
    await initialize_database_v2()
    async_db_manager.initialize()
    yield
    # Clean up

    # await drop_database()

    await async_db_manager.close()


app = FastAPI(lifespan=lifespan)

origins = [
    "http://localhost:5500",  # Port typique de Live Server (VS Code)
    "http://127.0.0.1:5500",
    "http://localhost:3000",  # Port typique pour React/Vue
    "http://localhost:8000",  # Votre propre backend
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Autorise ces origines
    allow_credentials=True,
    allow_methods=["*"],  # Autorise toutes les méthodes (GET, POST, etc.)
    allow_headers=["*"],  # Autorise tous les headers
)

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
