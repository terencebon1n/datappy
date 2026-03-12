from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.dependencies import async_db_manager
from src.api.v1.endpoints.transit import gtfs_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load
    async_db_manager.initialize()
    yield
    # Unload
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
            "src.api.__init__:app",
            host="0.0.0.0",
            port=8000,
            reload=False,
            log_level="info",
        )
