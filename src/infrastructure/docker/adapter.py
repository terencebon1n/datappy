import logging
from enum import StrEnum
from typing import Any

from docker.errors import NotFound

import docker
from src.domain.admin.process import ManagedProcess, ManagedServiceType, ProcessStatus
from src.domain.gtfs_rt.enums import City

logger = logging.getLogger(__name__)


class DockerContainerStatus(StrEnum):
    RUNNING = "running"
    EXITED = "exited"
    CREATED = "created"
    PAUSED = "paused"
    RESTARTING = "restarting"

    def to_process_status(self) -> ProcessStatus:
        match self:
            case DockerContainerStatus.RUNNING | DockerContainerStatus.RESTARTING:
                return ProcessStatus.RUNNING
            case DockerContainerStatus.EXITED:
                return ProcessStatus.CRASHED
            case _:
                return ProcessStatus.STOPPED


class DockerRestartPolicy(StrEnum):
    ON_FAILURE = "on-failure"
    ALWAYS = "always"
    UNLESS_STOPPED = "unless-stopped"
    NO = "no"

    def config(self, max_retries: int = 0) -> dict[str, Any]:
        return {"Name": self.value, "MaximumRetryCount": max_retries}


class DockerProcessAdapter:
    def __init__(self, image: str, network: str, host: str) -> None:
        self._host = host
        self._image = image
        self._network = network
        self.__client: docker.DockerClient | None = None

    @property
    def _client(self) -> docker.DockerClient:
        if self.__client is None:
            self.__client = docker.DockerClient(base_url=self._host)
        return self.__client

    def _container_name(self, service: ManagedServiceType, city: City) -> str:
        return f"datappy_{service}_{city}"

    def run_service(self, service: ManagedServiceType, city: City) -> ManagedProcess:
        name = self._container_name(service, city)
        try:
            self._client.containers.get(name).remove(force=True)
        except NotFound:
            pass
        logger.info("Is it crashing here ?")
        self._client.containers.run(
            self._image,
            command=["python", "-m", "main", service.value, city.value],
            name=name,
            detach=True,
            restart_policy=DockerRestartPolicy.ON_FAILURE.config(max_retries=5),
            network=self._network,
        )
        logger.info(f"Started container {name}")
        return ManagedProcess(
            service=service,
            city=city,
            status=ProcessStatus.RUNNING,
            container_name=name,
        )

    def stop_service(self, service: ManagedServiceType, city: City) -> None:
        name = self._container_name(service, city)
        try:
            container = self._client.containers.get(name)
            container.stop()
            container.remove()
            logger.info(f"Stopped container {name}")
        except NotFound:
            raise ValueError(f"No container found for {service} {city}")

    def close(self) -> None:
        if self.__client is not None:
            self.__client.close()
            self.__client = None

    def get_all_status(self) -> list[ManagedProcess]:
        result = []
        for service in ManagedServiceType:
            for city in City:
                name = self._container_name(service, city)
                try:
                    container = self._client.containers.get(name)
                    status = DockerContainerStatus(container.status).to_process_status()
                except (NotFound, ValueError):
                    status = ProcessStatus.STOPPED
                result.append(
                    ManagedProcess(
                        service=service,
                        city=city,
                        status=status,
                        container_name=name,
                    )
                )
        return result
