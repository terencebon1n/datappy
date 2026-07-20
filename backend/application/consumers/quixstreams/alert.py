from __future__ import annotations

from types import TracebackType
from typing import Optional, Type

from quixstreams.dataframe import StreamingDataFrame
from quixstreams.sinks import BaseSink

from backend.domain.gtfs_rt.enums import City, FeedType
from backend.infrastructure.processing.quixstreams.consumer import (
    QuixStreamsConsumerAdapter,
)


class QuixStreamsAlertStream:
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
        sdf = self.quix_adapter.stream(FeedType.ALERT.topic(self.city))

        sdf["alert_id"] = sdf.apply(lambda col: col["id"])

        sdf = sdf[
            [
                "alert_id",
                "active_periods",
                "informed_entities",
                "cause",
                "effect",
                "severity",
                "header_text",
                "description_text",
                "url",
            ]
        ]

        sdf.sink(self._sink)

        return sdf

    def run(self) -> None:
        self.quix_adapter.app.run()

    def __enter__(self) -> QuixStreamsAlertStream:
        self._process_dataframe()
        return self

    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_value: Optional[BaseException],
        traceback: Optional[TracebackType],
    ) -> None:
        self.quix_adapter.app.stop()
