from types import TracebackType
from typing import Optional, Type

import pyspark.sql.functions as sf
from pyspark.sql import DataFrame
from pyspark.sql.streaming.query import StreamingQuery

from src.infrastructure.database.redis.sink.stop_update import StopUpdateSink
from src.infrastructure.processing.spark.column import (
    KafkaColumns,
    StopTimeColumns,
    TripColumns,
    TripUpdateColumns,
)
from src.infrastructure.processing.spark.consumer import SparkConsumerAdapter
from src.infrastructure.processing.spark.schema import TRIP_UPDATE_SCHEMA


class StopUpdateStream:
    def __init__(
        self, spark_adapter: SparkConsumerAdapter, sink: StopUpdateSink
    ) -> None:
        self.spark_adapter = spark_adapter
        self.sink = sink

    def _process_dataframe(self) -> DataFrame:
        K, TU, T, ST = KafkaColumns, TripUpdateColumns, TripColumns, StopTimeColumns

        base_df: DataFrame = (
            self.spark_adapter.stream("TripUpdate")
            .select(
                K.KEY.col.cast("string").alias(K.KEY),
                K.TIMESTAMP.col.cast("timestamp").alias("event_time"),
                sf.from_json(K.VALUE.col.cast("string"), TRIP_UPDATE_SCHEMA).alias(
                    K.VALUE
                ),
            )
            .select(
                "event_time",
                (K.VALUE / TU.TRIP / T.ROUTE_ID).alias(T.ROUTE_ID),
                (K.VALUE / TU.TRIP / T.DIRECTION_ID).alias(T.DIRECTION_ID),
                (K.VALUE / TU.TRIP / T.ID).alias(T.TRIP_ID),
                (K.VALUE / TU.STOP_TIME / ST.STOP_ID).alias(ST.STOP_ID),
                (K.VALUE / TU.STOP_TIME / ST.DEPARTURE_TIME).alias(ST.DEPARTURE_TIME),
                (K.VALUE / TU.STOP_TIME / ST.DEPARTURE_DELAY).alias(ST.DEPARTURE_DELAY),
                (K.VALUE / TU.STOP_TIME / ST.ARRIVAL_TIME).alias(ST.ARRIVAL_TIME),
                (K.VALUE / TU.STOP_TIME / ST.ARRIVAL_DELAY).alias(ST.ARRIVAL_DELAY),
            )
        )

        return (
            base_df.withWatermark("event_time", "2 minutes")
            .groupBy(T.ROUTE_ID, T.DIRECTION_ID, ST.STOP_ID, T.TRIP_ID)
            .agg(
                sf.max("event_time").alias(K.TIMESTAMP),
                sf.last(ST.DEPARTURE_TIME).alias(ST.DEPARTURE_TIME),
                sf.last(ST.DEPARTURE_DELAY).alias(ST.DEPARTURE_DELAY),
                sf.last(ST.ARRIVAL_TIME).alias(ST.ARRIVAL_TIME),
                sf.last(ST.ARRIVAL_DELAY).alias(ST.ARRIVAL_DELAY),
            )
        )

    def __enter__(self) -> StreamingQuery:
        processed_df: DataFrame = self._process_dataframe()

        return (
            processed_df.writeStream.outputMode("update")
            .foreachBatch(self.sink.write_batch)
            .option("checkpointLocation", "/tmp/checkpoints/stop_update")
            .start()
        )

    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_value: Optional[BaseException],
        traceback: Optional[TracebackType],
    ) -> None:
        self.spark_adapter.spark.stop()
