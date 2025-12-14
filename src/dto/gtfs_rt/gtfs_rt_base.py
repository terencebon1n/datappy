from abc import abstractmethod
from typing import Type, TypeVar, cast, get_args
from google.transit import gtfs_realtime_pb2

TDataclass = TypeVar("TDataclass")


class GTFSRTContainerBase[TDataclass]:
    items: list[TDataclass]

    def __init__(self) -> None:
        self.items = []
        self.feed = gtfs_realtime_pb2.FeedMessage()  # type: ignore[attr-defined]

    @property
    def _resolve_dataclass(cls) -> TDataclass:
        return get_args(cls.__orig_bases__[0])[0]  # type: ignore[attr-defined]

    @property
    def _resolve_dataclass_type(cls) -> type[TDataclass]:
        return cast(Type[TDataclass], cls._resolve_dataclass)

    @abstractmethod
    async def extract(self, url: str) -> list[TDataclass]: ...
