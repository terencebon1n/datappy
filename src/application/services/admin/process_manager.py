from src.domain.admin.process import ManagedProcess, ManagedServiceType
from src.domain.gtfs_rt.enums import City
from src.infrastructure.docker.adapter import DockerProcessAdapter


class ProcessManagerService:
    def __init__(self, adapter: DockerProcessAdapter) -> None:
        self._adapter = adapter

    def start(self, service: ManagedServiceType, city: City) -> ManagedProcess:
        return self._adapter.run_service(service, city)

    def stop(self, service: ManagedServiceType, city: City) -> None:
        self._adapter.stop_service(service, city)

    def get_all_status(self) -> list[ManagedProcess]:
        return self._adapter.get_all_status()

    def close(self) -> None:
        self._adapter.close()
