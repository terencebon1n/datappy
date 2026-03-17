import asyncio
from inspect import iscoroutinefunction
from typing import Any, Callable, Dict, Optional

from src.application.services.enums import ServiceCommand
from src.domain.gtfs_rt.enums import City


class ServiceRegistry:
    def __init__(self) -> None:
        self._tasks: Dict[str, Callable[[], Any]] = {}

    def register(self, name: ServiceCommand, task: Callable[[], Any]) -> None:
        self._tasks[name] = task

    def run(self, name: str, city: Optional[str] = None) -> None:
        if name not in self._tasks:
            raise ValueError(f"Unknown service: {name}")

        service = self._tasks[name]()

        if iscoroutinefunction(service.start):
            if city:
                asyncio.run(service.start(City(city)))
            else:
                asyncio.run(service.start())
        else:
            if city:
                service.start(City(city))
            else:
                service.start()
