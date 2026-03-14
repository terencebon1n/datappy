import uvicorn


class ApiService:
    def start(self) -> None:
        uvicorn.run(
            "src.api.__init__:app",
            host="0.0.0.0",
            port=8000,
            reload=False,
            log_level="info",
        )
