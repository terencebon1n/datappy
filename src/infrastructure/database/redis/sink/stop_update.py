import json

from pyspark.sql import DataFrame

from src.infrastructure.database.redis.context import RedisPipelineContext
from src.infrastructure.processing.spark.column import (
    KafkaColumns,
    StopTimeColumns,
    TripColumns,
)


class StopUpdateSink:
    @staticmethod
    def _to_json_payload(row) -> str:
        payload = {
            "trip_id": row[TripColumns.TRIP_ID],
            "timestamp": str(row[KafkaColumns.TIMESTAMP]),
            "departure_time": row[StopTimeColumns.DEPARTURE_TIME],
            "departure_delay": row[StopTimeColumns.DEPARTURE_DELAY],
            "arrival_time": row[StopTimeColumns.ARRIVAL_TIME],
            "arrival_delay": row[StopTimeColumns.ARRIVAL_DELAY],
        }
        return json.dumps(payload)

    @classmethod
    def _process_partition(cls, partition) -> None:
        with RedisPipelineContext() as redis_ctx:
            for row in partition:
                redis_key = f"{row[TripColumns.ROUTE_ID]}:{row[TripColumns.DIRECTION_ID]}:{row[StopTimeColumns.STOP_ID]}"
                field_key = row[TripColumns.TRIP_ID]
                json_data = cls._to_json_payload(row)

                redis_ctx.add_to_pipeline(redis_key, field_key, json_data)

    def write_batch(self, batch_df: DataFrame, batch_id: int) -> None:
        """The entry point for Spark's .foreachBatch()"""
        if not batch_df.isEmpty():
            batch_df.foreachPartition(self._process_partition)
