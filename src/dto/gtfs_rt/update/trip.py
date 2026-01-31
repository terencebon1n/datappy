import logging
from dataclasses import dataclass

import requests
from pyspark.sql.types import (
    StructField,
    StructType,
)

from ..gtfs_rt_base import GTFSRTContainerBase, GTFSRTProducerBase
from ..spark_base import SparkColumns
from ..trip import Trip
from .stop_time import StopTime

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s:\t  %(message)s",
)

logger = logging.getLogger(__name__)


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
