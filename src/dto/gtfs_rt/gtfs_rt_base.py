import msgspec

from aiokafka import AIOKafkaProducer
from aiokafka.admin import AIOKafkaAdminClient, NewTopic
from pyspark.sql import SparkSession, DataFrame

from abc import abstractmethod
from typing import Type, TypeVar, cast, get_args
from google.transit import gtfs_realtime_pb2
from ...config import settings, AppConfig

TDataclass = TypeVar("TDataclass")


class GTFSRTStreamBase[TDataclass]:
    spark: SparkSession
    stream: DataFrame

    def __init__(self, appname: str) -> None:
        kafka_config = AppConfig.from_yaml("config.yaml").kafka.to_spark_options()
        kafka_config["subscribe"] = self._resolve_dataclass_type.__name__

        self.spark = (
            SparkSession.builder.remote("sc://localhost:15002")
            .appName(appname)
            .getOrCreate()
        )

        self.stream = (
            self.spark.readStream.format("kafka").options(**kafka_config).load()
        )

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

    async def __aenter__(self):
        await self.admin.start()
        await self.producer.start()
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        if self.producer:
            await self.producer.stop()

        return False

    async def create_topic(self):
        new_topics = [
            NewTopic(
                name=self._resolve_dataclass_type.__name__,
                num_partitions=1,
                replication_factor=1,
            )
        ]
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
