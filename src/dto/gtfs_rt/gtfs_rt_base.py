import logging
from abc import abstractmethod
from typing import Type, TypeVar, cast, get_args

import msgspec
from aiokafka import AIOKafkaProducer
from aiokafka.admin import AIOKafkaAdminClient, NewTopic
from google.transit import gtfs_realtime_pb2
from pyspark.sql import SparkSession

from ...config import AppConfig, settings

TDataclass = TypeVar("TDataclass")


logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s:\t  %(message)s",
)

logger = logging.getLogger(__name__)


class GTFSRTStreamBase[TDataclass]:
    spark: SparkSession
    config: AppConfig

    def __init__(self, appname: str) -> None:
        self.config = AppConfig.from_yaml("config.yaml")

        self.spark = (
            SparkSession.builder.remote("sc://localhost:15002")
            .appName(appname)
            .getOrCreate()
        )

        self.spark.conf.set("spark.sql.shuffle.partitions", "4")
        self.spark.conf.set("spark.sql.session.timeZone", "UTC")

    @property
    def _resolve_dataclass(cls) -> TDataclass:
        return get_args(cls.__orig_bases__[0])[0]  # type: ignore[attr-defined]

    @property
    def _resolve_dataclass_type(cls) -> type[TDataclass]:
        return cast(Type[TDataclass], cls._resolve_dataclass)


class GTFSRTProducerBase[TDataclass]:
    producer: AIOKafkaProducer

    def __init__(self) -> None:
        self.admin = AIOKafkaAdminClient(
            bootstrap_servers=settings.kafka.brokers,
        )
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

    async def start(self):
        await self.admin.start()
        await self.producer.start()
        return self

    async def stop(self):
        if self.producer:
            await self.producer.stop()

        return False

    async def __aenter__(self):
        return await self.start()

    async def __aexit__(self, exc_type, exc_value, traceback):
        return await self.stop()

    async def create_topic(self):
        configs = {
            "cleanup.policy": "compact",
        }

        new_topics = [
            NewTopic(
                name=self._resolve_dataclass_type.__name__,
                num_partitions=1,
                replication_factor=1,
                topic_configs=configs,
            )
        ]

        logger.info(f"Creating topic {self._resolve_dataclass_type.__name__}")

        await self.admin.create_topics(new_topics=new_topics)

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
