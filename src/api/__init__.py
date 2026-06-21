from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.dependencies import async_db_manager, process_manager
from src.api.v1.endpoints.admin import admin_router
from src.api.v1.endpoints.transit import basic_router, gtfs_router, gtfs_rt_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    async_db_manager.initialize()
    yield
    await async_db_manager.close()
    process_manager.close()


app = FastAPI(lifespan=lifespan)

origins = [
    "http://localhost:5500",
    "http://127.0.0.1:5500",
    "http://localhost:3000",
    "http://localhost:8000",
    "http://localhost:8001",
    "http://127.0.0.1:8001",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Autorise ces origines
    allow_credentials=True,
    allow_methods=["*"],  # Autorise toutes les méthodes (GET, POST, etc.)
    allow_headers=["*"],  # Autorise tous les headers
)

app.include_router(basic_router)
app.include_router(gtfs_router)
app.include_router(gtfs_rt_router)
app.include_router(admin_router)
