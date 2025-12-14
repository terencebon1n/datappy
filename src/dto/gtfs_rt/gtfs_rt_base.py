import msgspec

from aiokafka import AIOKafkaProducer

from abc import abstractmethod
from typing import Type, TypeVar, cast, get_args
from google.transit import gtfs_realtime_pb2
from ...config import settings

TDataclass = TypeVar("TDataclass")


class GTFSRTProducerBase[TDataclass]:
    producer: AIOKafkaProducer

    def __init__(self) -> None:
        self.producer = AIOKafkaProducer(
            bootstrap_servers=settings.kafka.brokers,
        )
        self.encoder = msgspec.json.Encoder()

    @property
    def _resolve_dataclass(cls) -> TDataclass:
        return get_args(cls.__orig_bases__[0])[0]  # type: ignore[attr-defined]

    @property
    def _resolve_dataclass_type(cls) -> type[TDataclass]:
        return cast(Type[TDataclass], cls._resolve_dataclass)

    async def __aenter__(self):
        await self.producer.start()
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        if self.producer:
            await self.producer.stop()

        return False

    @abstractmethod
    async def send_dataclass(self, event: TDataclass): ...


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
