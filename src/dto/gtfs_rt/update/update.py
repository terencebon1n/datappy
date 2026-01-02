from dataclasses import dataclass
import time

import requests
import pyspark.sql.functions as sf
from pyspark.sql.types import (
    StructField,
    StructType,
)

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

    def deserialize(self):
        KR, TU, T, ST = KafkaRawColumns, TripUpdateColumns, TripColumns, StopTimeColumns

        new_stream = (
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

        query = (
            new_stream.writeStream.outputMode("update")
            .queryName("trip_updates")
            .format("memory")
            .start()
        )

        for _ in range(20):
            self.spark.sql("SELECT * FROM trip_updates ORDER BY route_id").show()
            time.sleep(5)


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
