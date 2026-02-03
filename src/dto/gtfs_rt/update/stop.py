import json
import logging
from dataclasses import dataclass

import pyspark.sql.functions as sf
import redis
from pyspark.sql import DataFrame
from pyspark.sql.streaming.query import StreamingQuery

from ..gtfs_rt_base import GTFSRTStreamBase
from ..spark_base import SparkColumns
from ..trip import TripColumns
from .stop_time import StopTimeColumns
from .trip import MinimizedTripUpdate, TripUpdate, TripUpdateColumns

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s:\t  %(message)s",
)

logger = logging.getLogger(__name__)


class KafkaRawColumns(SparkColumns):
    KEY = "key"
    VALUE = "value"
    TIMESTAMP = "timestamp"


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

        base_df: DataFrame = self.stream.select(
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
                sf.max("event_time").alias(KR.TIMESTAMP),
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
                redis_key = f"{row[TripColumns.ROUTE_ID]}:{row[TripColumns.DIRECTION_ID]}:{row[StopTimeColumns.STOP_ID]}"
                field_key = row[TripColumns.TRIP_ID]

                payload = {
                    "trip_id": row[TripColumns.TRIP_ID],
                    "timestamp": str(row[KafkaRawColumns.TIMESTAMP]),
                    "departure_time": row[StopTimeColumns.DEPARTURE_TIME],
                    "departure_delay": row[StopTimeColumns.DEPARTURE_DELAY],
                    "arrival_time": row[StopTimeColumns.ARRIVAL_TIME],
                    "arrival_delay": row[StopTimeColumns.ARRIVAL_DELAY],
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
        processed_df: DataFrame = self.process_dataframe()

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
