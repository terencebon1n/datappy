from pyspark.sql.types import (
    IntegerType,
    StringType,
    StructField,
    StructType,
)

from ..column import StopTimeColumns

STOP_TIME_SCHEMA = StructType(
    [
        StructField(StopTimeColumns.STOP_ID, StringType(), True),
        StructField(StopTimeColumns.ARRIVAL_DELAY, IntegerType(), True),
        StructField(StopTimeColumns.ARRIVAL_TIME, IntegerType(), True),
        StructField(StopTimeColumns.DEPARTURE_DELAY, IntegerType(), True),
        StructField(StopTimeColumns.DEPARTURE_TIME, IntegerType(), True),
        StructField(StopTimeColumns.SCHEDULE_RELATIONSHIP, StringType(), True),
    ]
)
