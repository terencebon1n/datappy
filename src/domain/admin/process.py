from enum import StrEnum

from pydantic import BaseModel

from src.domain.gtfs_rt.enums import City


class ManagedServiceType(StrEnum):
    PRODUCER = "producer"
    CONSUMER = "consumer"


class ProcessStatus(StrEnum):
    RUNNING = "running"
    STOPPED = "stopped"
    CRASHED = "crashed"


class ManagedProcess(BaseModel):
    service: ManagedServiceType
    city: City
    status: ProcessStatus
    container_name: str
