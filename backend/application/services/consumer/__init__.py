from backend.application.consumers.quixstreams.stop_update import (
    QuixStreamsStopUpdateStream,
)
from backend.domain.gtfs_rt.enums import City
from backend.infrastructure.config import settings
from backend.infrastructure.database.redis.sink import RedisHsetStopUpdateSink
from backend.infrastructure.processing.quixstreams.consumer import (
    QuixStreamsConsumerAdapter,
)


class QuixStreamsConsumerService:
    def start(self, city: City) -> None:
        quix = QuixStreamsConsumerAdapter(consumer_group=f"stop-update-{city}")
        sink = RedisHsetStopUpdateSink(
            city=city,
            host=settings.redis.host,
            port=settings.redis.port,
        )
        with QuixStreamsStopUpdateStream(quix, city, sink) as stream:
            stream.run()
