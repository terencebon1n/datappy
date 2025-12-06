import uvicorn
from fastapi import FastAPI

from .router import gtfs_router


app = FastAPI()

app.include_router(gtfs_router)


class BackEnd:
    def start(self) -> None:
        uvicorn.run(
            "src.backend.__init__:app",
            host="0.0.0.0",
            port=8000,
            reload=True,  # Enables auto-reloading during development
            log_level="info",
        )
