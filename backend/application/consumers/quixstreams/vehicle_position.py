from __future__ import annotations

from types import TracebackType
from typing import Optional, Type

from quixstreams.dataframe import StreamingDataFrame
from quixstreams.sinks import BaseSink

from backend.domain.gtfs_rt.enums import City, FeedType
from backend.infrastructure.processing.quixstreams.consumer import (
    QuixStreamsConsumerAdapter,
)


class QuixStreamsVehiclePositionStream:
    def __init__(
        self,
        quix_adapter: QuixStreamsConsumerAdapter,
        city: City,
        sink: BaseSink,
    ) -> None:
        self.quix_adapter = quix_adapter
        self.city = city
        self._sink = sink

    def _process_dataframe(self) -> StreamingDataFrame:
        sdf = self.quix_adapter.stream(FeedType.VEHICLE_POSITION.topic(self.city))

        sdf["vehicle_id"] = sdf.apply(lambda col: col["id"])
        sdf["trip_id"] = sdf.apply(lambda col: col["trip"]["id"])
        sdf["route_id"] = sdf.apply(lambda col: col["trip"]["route_id"])
        sdf["direction_id"] = sdf.apply(lambda col: col["trip"]["direction_id"])
        sdf["schedule_relationship"] = sdf.apply(
            lambda col: col["trip"]["schedule_relationship"]
        )
        sdf["latitude"] = sdf.apply(lambda col: col["position"]["latitude"])
        sdf["longitude"] = sdf.apply(lambda col: col["position"]["longitude"])
        sdf["bearing"] = sdf.apply(lambda col: col["position"]["bearing"])
        sdf["speed"] = sdf.apply(lambda col: col["position"]["speed"])

        sdf = sdf[
            [
                "vehicle_id",
                "trip_id",
                "route_id",
                "direction_id",
                "schedule_relationship",
                "latitude",
                "longitude",
                "bearing",
                "speed",
                "current_status",
                "timestamp",
            ]
        ]

        sdf.sink(self._sink)

        return sdf

    def run(self) -> None:
        self.quix_adapter.app.run()

    def __enter__(self) -> QuixStreamsVehiclePositionStream:
        self._process_dataframe()
        return self

    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_value: Optional[BaseException],
        traceback: Optional[TracebackType],
    ) -> None:
        self.quix_adapter.app.stop()
