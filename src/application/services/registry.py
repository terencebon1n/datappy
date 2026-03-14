import asyncio
from inspect import iscoroutinefunction
from typing import Any, Callable, Dict

from src.application.services.enums import ServiceCommand


class ServiceRegistry:
    def __init__(self) -> None:
        self._tasks: Dict[str, Callable[[], Any]] = {}

    def register(self, name: ServiceCommand, task: Callable[[], Any]) -> None:
        self._tasks[name] = task

    def run(self, name: str) -> None:
        if name not in self._tasks:
            raise ValueError(f"Unknown service: {name}")

        service = self._tasks[name]()

        if iscoroutinefunction(service.start):
            asyncio.run(service.start())
        else:
            service.start()
