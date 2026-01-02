from dataclasses import dataclass

from pyspark.sql.types import (
    IntegerType,
    StringType,
    StructField,
    StructType,
)
from ...spark_base import SparkColumns


class StopTimeColumns(SparkColumns):
    STOP_ID = "stop_id"
    ARRIVAL_DELAY = "arrival_delay"
    ARRIVAL_TIME = "arrival_time"
    DEPARTURE_DELAY = "departure_delay"
    DEPARTURE_TIME = "departure_time"
    SCHEDULE_RELATIONSHIP = "schedule_relationship"


@dataclass(frozen=True)
class StopTime:
    stop_id: str
    arrival_delay: int
    arrival_time: int
    departure_delay: int
    departure_time: int
    schedule_relationship: str

    @classmethod
    def schema(cls) -> StructType:
        return StructType(
            [
                StructField(StopTimeColumns.STOP_ID, StringType(), True),
                StructField(StopTimeColumns.ARRIVAL_DELAY, IntegerType(), True),
                StructField(StopTimeColumns.ARRIVAL_TIME, IntegerType(), True),
                StructField(StopTimeColumns.DEPARTURE_DELAY, IntegerType(), True),
                StructField(StopTimeColumns.DEPARTURE_TIME, IntegerType(), True),
                StructField(StopTimeColumns.SCHEDULE_RELATIONSHIP, StringType(), True),
            ]
        )
