from pyspark.sql.types import (
    IntegerType,
    StringType,
    StructField,
    StructType,
)

from ..column import TripColumns

TRIP_SCHEMA = StructType(
    [
        StructField(TripColumns.ID, StringType(), True),
        StructField(TripColumns.SCHEDULE_RELATIONSHIP, StringType(), True),
        StructField(TripColumns.ROUTE_ID, StringType(), True),
        StructField(TripColumns.DIRECTION_ID, IntegerType(), True),
    ]
)
