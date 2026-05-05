from __future__ import annotations

from types import TracebackType
from typing import Optional, Type

from quixstreams.dataframe import StreamingDataFrame

from src.domain.gtfs_rt.enums import City
from src.infrastructure.processing.quixstreams.consumer import (
    QuixStreamsConsumerAdapter,
)


class QuixStreamsStopUpdateStream:
    def __init__(self, quix_adapter: QuixStreamsConsumerAdapter, city: City) -> None:
        self.quix_adapter = quix_adapter
        self.city = city

    def _process_dataframe(self) -> StreamingDataFrame:
        sdf = self.quix_adapter.stream("TripUpdate")

        sdf["trip_id"] = sdf.apply(lambda col: col["trip"]["id"])
        sdf["route_id"] = sdf.apply(lambda col: col["trip"]["route_id"])
        sdf["direction_id"] = sdf.apply(lambda col: col["trip"]["direction_id"])
        sdf["stop_id"] = sdf.apply(lambda col: col["stop_time"]["id"])
        sdf["group_id"] = sdf.apply(
            lambda col: (
                f"{self.city}:{col['route_id']}:{col['direction_id']}:{col['stop_id']}:{col['trip_id']}"
            )
        )

        sdf["timestamp"] = sdf.apply(
            lambda value, key, timestamp, headers: timestamp, metadata=True
        )
        sdf["departure_time"] = sdf.apply(
            lambda col: col["stop_time"]["departure_time"]
        )
        sdf["departure_delay"] = sdf.apply(
            lambda col: col["stop_time"]["departure_delay"]
        )
        sdf["arrival_time"] = sdf.apply(lambda col: col["stop_time"]["arrival_time"])
        sdf["arrival_delay"] = sdf.apply(lambda col: col["stop_time"]["arrival_delay"])

        sdf = sdf.group_by("group_id")

        sdf = sdf[
            [
                "trip_id",
                "route_id",
                "direction_id",
                "stop_id",
                "timestamp",
                "departure_time",
                "departure_delay",
                "arrival_time",
                "arrival_delay",
            ]
        ]

        self.quix_adapter.sink(sdf)

        return sdf

    def run(self) -> None:
        self.quix_adapter.app.run()

    def __enter__(self) -> QuixStreamsStopUpdateStream:
        self._process_dataframe()
        return self

    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_value: Optional[BaseException],
        traceback: Optional[TracebackType],
    ) -> None:
        self.quix_adapter.app.stop()
