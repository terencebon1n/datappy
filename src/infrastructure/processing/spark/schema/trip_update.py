from pyspark.sql.types import (
    StructField,
    StructType,
)

from ..column import TripUpdateColumns
from .stop_time import STOP_TIME_SCHEMA
from .trip import TRIP_SCHEMA

TRIP_UPDATE_SCHEMA = StructType(
    [
        StructField(TripUpdateColumns.TRIP, TRIP_SCHEMA, True),
        StructField(TripUpdateColumns.STOP_TIME, STOP_TIME_SCHEMA, True),
    ]
)
