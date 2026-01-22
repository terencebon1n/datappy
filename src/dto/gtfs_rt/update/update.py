from dataclasses import dataclass

import pyspark.sql.functions as sf
import redis
import requests
from pyspark.sql import DataFrame
from pyspark.sql.types import (
    StructField,
    StructType,
)
from pyspark.sql.streaming.query import StreamingQuery

from ..gtfs_rt_base import GTFSRTContainerBase, GTFSRTProducerBase, GTFSRTStreamBase
from ..spark_base import SparkColumns
from ..trip import Trip, TripColumns
from .stop_time import StopTime, StopTimeColumns


class KafkaRawColumns(SparkColumns):
    KEY = "key"
    VALUE = "value"


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


class StopUpdateStream(GTFSRTStreamBase[TripUpdate]):
    def __init__(self, appname: str) -> None:
        super().__init__(appname)

        self.stream: DataFrame = (
            self.spark.readStream.format("kafka")
            .options(**self.config.kafka.to_spark_options())
            .option("subscribe", self._resolve_dataclass_type.__name__)
            .load()
        )

    def process_dataframe(self) -> DataFrame:
        KR, TU, T, ST = KafkaRawColumns, TripUpdateColumns, TripColumns, StopTimeColumns

        return (
            self.stream.select(
                KR.KEY.col.cast("string").alias(KR.KEY),
                sf.from_json(
                    KR.VALUE.col.cast("string"), MinimizedTripUpdate.schema()
                ).alias(KR.VALUE),
            )
            .select(
                KR.KEY.col,
                (KR.VALUE / TU.TRIP / T.ROUTE_ID).alias(T.ROUTE_ID),
                (KR.VALUE / TU.TRIP / T.DIRECTION_ID).alias(T.DIRECTION_ID),
                (KR.VALUE / TU.TRIP / T.ID).alias(T.TRIP_ID),
                (KR.VALUE / TU.STOP_TIME / ST.STOP_ID).alias(ST.STOP_ID),
                (KR.VALUE / TU.STOP_TIME / ST.DEPARTURE_TIME).alias(ST.DEPARTURE_TIME),
                (KR.VALUE / TU.STOP_TIME / ST.DEPARTURE_DELAY).alias(
                    ST.DEPARTURE_DELAY
                ),
                (KR.VALUE / TU.STOP_TIME / ST.ARRIVAL_TIME).alias(ST.ARRIVAL_TIME),
                (KR.VALUE / TU.STOP_TIME / ST.ARRIVAL_DELAY).alias(ST.ARRIVAL_DELAY),
            )
            .groupBy(T.ROUTE_ID, T.DIRECTION_ID, ST.STOP_ID)
            .agg(
                sf.collect_set(
                    sf.struct(
                        T.TRIP_ID,
                        ST.DEPARTURE_TIME,
                        ST.DEPARTURE_DELAY,
                        ST.ARRIVAL_TIME,
                        ST.ARRIVAL_DELAY,
                    )
                ).alias("stop_times")
            )
            .withColumn("stop_times", sf.to_json(sf.col("stop_times")))
        )

    @staticmethod
    def _write_to_redis_batch(batch_df: DataFrame, batch_id: int):
        """
        Internal worker function to process one micro-batch.
        """

        def process_partition(partition):
            # Connect to the 'redis' service defined in your docker-compose
            r = redis.Redis(host="redis", port=6379, decode_responses=True)
            pipe = r.pipeline()

            for row in partition:
                # 1. Create the composite key
                redis_key = f"{row['route_id']}:{row['direction_id']}:{row['stop_id']}"

                # 2. Overwrite logic
                # We use a simple SET because stop_times is already a JSON string
                # from your sf.to_json transformation.
                pipe.set(redis_key, row["stop_times"])

                # 3. Optional: Set TTL to 5 minutes (300s) so stale real-time data expires
                pipe.expire(redis_key, 300)

            pipe.execute()

        batch_df.foreachPartition(process_partition)

    def to_redis(self) -> StreamingQuery:
        """
        Starts the stream and sinks data to Redis.
        """
        processed_df = self.process_dataframe()

        # Using 'update' mode is appropriate here since you are using aggregations (groupBy)
        return (
            processed_df.writeStream.outputMode("update")
            .foreachBatch(self._write_to_redis_batch)
            .option("checkpointLocation", f"/tmp/checkpoints/{self.__class__.__name__}")
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
