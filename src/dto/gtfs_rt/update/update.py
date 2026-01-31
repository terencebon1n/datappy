import json
import logging
from dataclasses import dataclass

import pyspark.sql.functions as sf
import redis
import requests
from pyspark.sql import DataFrame
from pyspark.sql.streaming.query import StreamingQuery
from pyspark.sql.types import (
    StructField,
    StructType,
)

from ..gtfs_rt_base import GTFSRTContainerBase, GTFSRTProducerBase, GTFSRTStreamBase
from ..spark_base import SparkColumns
from ..trip import Trip, TripColumns
from .stop_time import StopTime, StopTimeColumns

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s:\t  %(message)s",
)

logger = logging.getLogger(__name__)


class KafkaRawColumns(SparkColumns):
    KEY = "key"
    VALUE = "value"
    TIMESTAMP = "timestamp"


class TripUpdateColumns(SparkColumns):
    ID = "id"
    TRIP = "trip"
    STOP_TIME = "stop_time"


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

    @classmethod
    def schema(cls) -> StructType:
        TU = TripUpdateColumns

        return StructType(
            [
                StructField(TU.TRIP, Trip.schema(), True),
                StructField(TU.STOP_TIME, StopTime.schema(), True),
            ]
        )


@dataclass(frozen=True)
class StopUpdate:
    trip_id: str
    timestamp: str
    departure_time: int
    departure_delay: int
    arrival_time: int
    arrival_delay: int


class StopUpdateStream(GTFSRTStreamBase[TripUpdate]):
    def __init__(self, appname: str) -> None:
        super().__init__(appname)

        self.stream: DataFrame = (
            self.spark.readStream.format("kafka")
            .options(**self.config.kafka.to_spark_options())
            .option("subscribe", self._resolve_dataclass_type.__name__)
            .option("failOnDataLoss", "false")
            .load()
        )

    def process_dataframe(self) -> DataFrame:
        KR, TU, T, ST = KafkaRawColumns, TripUpdateColumns, TripColumns, StopTimeColumns

        base_df = self.stream.select(
            KR.KEY.col.cast("string").alias(KR.KEY),
            KR.TIMESTAMP.col.cast("timestamp").alias("event_time"),
            sf.from_json(
                KR.VALUE.col.cast("string"), MinimizedTripUpdate.schema()
            ).alias(KR.VALUE),
        ).select(
            "event_time",
            (KR.VALUE / TU.TRIP / T.ROUTE_ID).alias(T.ROUTE_ID),
            (KR.VALUE / TU.TRIP / T.DIRECTION_ID).alias(T.DIRECTION_ID),
            (KR.VALUE / TU.TRIP / T.ID).alias(T.TRIP_ID),
            (KR.VALUE / TU.STOP_TIME / ST.STOP_ID).alias(ST.STOP_ID),
            (KR.VALUE / TU.STOP_TIME / ST.DEPARTURE_TIME).alias(ST.DEPARTURE_TIME),
            (KR.VALUE / TU.STOP_TIME / ST.DEPARTURE_DELAY).alias(ST.DEPARTURE_DELAY),
            (KR.VALUE / TU.STOP_TIME / ST.ARRIVAL_TIME).alias(ST.ARRIVAL_TIME),
            (KR.VALUE / TU.STOP_TIME / ST.ARRIVAL_DELAY).alias(ST.ARRIVAL_DELAY),
        )

        return (
            base_df.withWatermark("event_time", "2 minutes")
            .groupBy(T.ROUTE_ID, T.DIRECTION_ID, ST.STOP_ID, T.TRIP_ID)
            .agg(
                sf.max("event_time").alias("timestamp"),
                sf.last(ST.DEPARTURE_TIME).alias(ST.DEPARTURE_TIME),
                sf.last(ST.DEPARTURE_DELAY).alias(ST.DEPARTURE_DELAY),
                sf.last(ST.ARRIVAL_TIME).alias(ST.ARRIVAL_TIME),
                sf.last(ST.ARRIVAL_DELAY).alias(ST.ARRIVAL_DELAY),
            )
        )

    @staticmethod
    def _write_to_redis_batch(batch_df: DataFrame, batch_id: int):
        record_count = batch_df.count()
        logger.info(
            f"=== Batch {batch_id} started | Records to process: {record_count} ==="
        )

        def process_partition(partition):
            r = redis.Redis(host="redis", port=6379, decode_responses=True)
            pipe = r.pipeline()

            processed_in_partition = 0
            for row in partition:
                redis_key = f"{row['route_id']}:{row['direction_id']}:{row['stop_id']}"
                field_key = row["trip_id"]

                payload = {
                    "trip_id": row["trip_id"],
                    "timestamp": str(row["timestamp"]),
                    "departure_time": row["departure_time"],
                    "departure_delay": row["departure_delay"],
                    "arrival_time": row["arrival_time"],
                    "arrival_delay": row["arrival_delay"],
                }

                pipe.hset(redis_key, field_key, json.dumps(payload))
                pipe.expire(redis_key, 300)
                processed_in_partition += 1

            pipe.execute()
            print(f"DEBUG: Partition processed {processed_in_partition} records.")

        if record_count > 0:
            batch_df.foreachPartition(process_partition)

        logger.info(f"=== Batch {batch_id} completed ===")

    def to_redis(self) -> StreamingQuery:
        """
        Starts the stream and sinks data to Redis.
        """
        processed_df = self.process_dataframe()

        logger.info("Writing Stop Updates to Redis stream")

        # Using 'update' mode is appropriate here since you are using aggregations (groupBy)
        return (
            processed_df.writeStream.outputMode("update")
            .foreachBatch(self._write_to_redis_batch)
            .option(
                "checkpointLocation", f"/tmp/checkpoints/{self.__class__.__name__}_v2"
            )
            .start()
        )


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
