import uvicorn
from fastapi import FastAPI

from .router import test_router

app = FastAPI()

app.include_router(test_router)


class BackEnd:
    def start(self) -> None:
        uvicorn.run(
            "backend.__init__:app",
            host="0.0.0.0",
            port=8000,
            reload=True,  # Enables auto-reloading during development
            log_level="info",
        )
