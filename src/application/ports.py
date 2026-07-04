from typing import Any, Iterator, Protocol, Sequence

from src.domain.admin.process import ManagedProcess, ManagedServiceType
from src.domain.gtfs.enums import GTFSFileNames
from src.domain.gtfs_rt.enums import City
from src.domain.gtfs_rt.stop_update import StopUpdate
from src.domain.gtfs_rt.trip_update import TripUpdate


class ConveyanceReader(Protocol):
    async def get_conveyances(self) -> Sequence[Any]: ...


class StopNameReader(Protocol):
    async def get_stop_names(self, route_id: str) -> Sequence[str]: ...


class DirectionReader(Protocol):
    async def get_direction(
        self, route_id: str, origin_name: str, destination_name: str
    ) -> dict: ...


class StopUpdateReader(Protocol):
    async def get_stop_updates(
        self, city: City, route_id: str, direction_id: int, stop_id: str
    ) -> list[StopUpdate]: ...


class ReachableTripReader(Protocol):
    async def get_reachable_trip_ids(
        self, trip_ids: list[str], destination_stop_id: str
    ) -> Sequence[str]: ...


class TripUpdateSource(Protocol):
    async def fetch_rt(self, url: str) -> bytes: ...

    def parse_feed(self, payload: bytes) -> list[TripUpdate]: ...


class MessageProducer(Protocol):
    async def send(self, topic: str, key: str, value: bytes) -> None: ...


class ProcessAdapter(Protocol):
    def run_service(
        self, service: ManagedServiceType, city: City
    ) -> ManagedProcess: ...

    def stop_service(self, service: ManagedServiceType, city: City) -> None: ...

    def get_all_status(self) -> list[ManagedProcess]: ...

    def close(self) -> None: ...


class GTFSScheduleSource(Protocol):
    def contains(self, filename: GTFSFileNames) -> bool: ...

    def stream_csv(self, filename: GTFSFileNames) -> Iterator[dict]: ...
