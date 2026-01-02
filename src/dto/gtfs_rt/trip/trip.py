from dataclasses import dataclass
from pyspark.sql.types import (
    IntegerType,
    StringType,
    StructField,
    StructType,
)
from ..spark_base import SparkColumns


class TripColumns(SparkColumns):
    ID = "id"
    TRIP_ID = "trip_id"
    SCHEDULE_RELATIONSHIP = "schedule_relationship"
    ROUTE_ID = "route_id"
    DIRECTION_ID = "direction_id"


@dataclass(frozen=True)
class Trip:
    id: str
    schedule_relationship: str
    route_id: str
    direction_id: int

    @classmethod
    def schema(cls) -> StructType:
        return StructType(
            [
                StructField(TripColumns.ID, StringType(), True),
                StructField(TripColumns.SCHEDULE_RELATIONSHIP, StringType(), True),
                StructField(TripColumns.ROUTE_ID, StringType(), True),
                StructField(TripColumns.DIRECTION_ID, IntegerType(), True),
            ]
        )
