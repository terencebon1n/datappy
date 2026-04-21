from src.application.consumers.quixstreams.stop_update import (
    QuixStreamsStopUpdateStream,
)
from src.domain.gtfs_rt.enums import City
from src.infrastructure.processing.quixstreams.consumer import (
    QuixStreamsConsumerAdapter,
)


class QuixStreamsConsumerService:
    def start(self, city: City) -> None:
        quix = QuixStreamsConsumerAdapter()
        with QuixStreamsStopUpdateStream(quix, city) as stream:
            stream.run()
