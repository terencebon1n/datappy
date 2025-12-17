from dataclasses import dataclass
import time

import requests
from pyspark.sql import Row, SparkSession
from pyspark.sql.functions import col, from_json
from pyspark.sql.types import (
    ArrayType,
    DoubleType,
    IntegerType,
    StringType,
    StructField,
    StructType,
)

from ....config import settings
from ..gtfs_rt_base import GTFSRTContainerBase, GTFSRTProducerBase
from ..trip import Trip
from .stop_time import StopTime


@dataclass(frozen=True)
class TripUpdate:
    id: str
    trip: Trip
    stop_times: list[StopTime]


@dataclass(frozen=True)
class MinimizedTripUpdate:
    id: str
    trip: Trip
    stop_time: StopTime


@dataclass(frozen=True)
class StopArrival:
    trip_id: str
    time: int
    delay: int


@dataclass(frozen=True)
class StopDeparture:
    trip_id: str
    time: int
    delay: int


@dataclass(frozen=True)
class StopTripUpdate:
    route_id: str
    direction_id: str
    stop_id: str
    arrival: list[StopArrival]
    departure: list[StopDeparture]


trip_data_schema = StructType(
    [
        StructField("trip_id", StringType(), True),
        StructField("schedule_relationship", StringType(), True),
        StructField("route_id", StringType(), True),
        StructField("direction_id", IntegerType(), True),
    ]
)

stop_time_data_schema = StructType(
    [
        StructField("stop_id", StringType(), True),
        StructField("arrival_delay", IntegerType(), True),
        StructField("arrival_time", IntegerType(), True),
        StructField("departure_delay", IntegerType(), True),
        StructField("departure_time", IntegerType(), True),
        StructField("schedule_relationship", StringType(), True),
    ]
)

trip_update_value_schema = StructType(
    [
        StructField("trip", trip_data_schema, True),
        StructField("stop_time", stop_time_data_schema, True),
    ]
)


class TripUpdateSparkStream:
    def __init__(self) -> None:
        self.spark = (
            SparkSession.builder.remote("sc://localhost:15002")
            .appName("TripUpdateSparkStream")
            .getOrCreate()
        )

        self.stream = (
            self.spark.readStream.format("kafka")
            .option("kafka.bootstrap.servers", "broker:29092")
            .option("subscribe", "TripUpdate")
            .option("startingOffsets", "earliest")
            .load()
        )

    def deserialize(self):
        new_stream = self.stream.select(
            col("key").cast("string").alias("key"),
            from_json(col("value").cast("string"), trip_update_value_schema).alias(
                "value"
            ),
        ).select(
            col("key"),
            col("value.trip.route_id").alias("route_id"),
            col("value.trip.direction_id").alias("direction_id"),
            col("value.stop_time.stop_id").alias("stop_id"),
            col("value.stop_time.departure_time").alias("departure_time"),
            col("value.stop_time.departure_delay").alias("departure_delay"),
            col("value.stop_time.arrival_time").alias("arrival_time"),
            col("value.stop_time.arrival_delay").alias("arrival_delay"),
        )

        # query = new_stream.writeStream.queryName("trip_updates").format("memory").start()

        new_stream.writeStream.queryName("trip_updates").format("memory").start()

        for _ in range(5):
            self.spark.sql("SELECT * FROM trip_updates").show()
            time.sleep(5)


class TripUpdateEventProducer(GTFSRTProducerBase[TripUpdate]):
    def __init__(self) -> None:
        super().__init__()

    async def send_dataclass(self, event: TripUpdate):
        for stop_time in event.stop_times:
            await self.producer.send(
                topic=self._resolve_dataclass_type.__name__,
                key=f"{event.trip.route_id}_{event.trip.direction_id}_{stop_time.stop_id}".encode(
                    "utf-8"
                ),
                value=self.encoder.encode(
                    MinimizedTripUpdate(
                        id=event.id, trip=event.trip, stop_time=stop_time
                    )
                ),
            )


class TripUpdateContainer(GTFSRTContainerBase[TripUpdate]):
    items: list[TripUpdate]

    def __init__(self) -> None:
        super().__init__()

    async def extract(self, url: str) -> list[TripUpdate]:
        response = requests.get(url)
        self.feed.ParseFromString(response.content)
        for entity in self.feed.entity:
            stop_time_list: list[StopTime] = []
            for stop_time in entity.trip_update.stop_time_update:
                stop_time_list.append(
                    StopTime(
                        stop_id=stop_time.stop_id,
                        arrival_delay=stop_time.arrival.delay,
                        arrival_time=stop_time.arrival.time,
                        departure_delay=stop_time.departure.delay,
                        departure_time=stop_time.departure.time,
                        schedule_relationship=stop_time.schedule_relationship,
                    )
                )
            self.items.append(
                TripUpdate(
                    id=entity.id,
                    trip=Trip(
                        id=entity.trip_update.trip.trip_id,
                        schedule_relationship=entity.trip_update.trip.schedule_relationship,
                        route_id=entity.trip_update.trip.route_id,
                        direction_id=entity.trip_update.trip.direction_id,
                    ),
                    stop_times=stop_time_list,
                )
            )
        return self.items
