from src.application.consumers.quixstreams.stop_update import (
    QuixStreamsStopUpdateStream,
)
from src.domain.gtfs_rt.enums import City
from src.infrastructure.config import settings
from src.infrastructure.database.redis.sink import RedisHsetStopUpdateSink
from src.infrastructure.processing.quixstreams.consumer import (
    QuixStreamsConsumerAdapter,
)


class QuixStreamsConsumerService:
    def start(self, city: City) -> None:
        quix = QuixStreamsConsumerAdapter()
        sink = RedisHsetStopUpdateSink(
            city=city,
            host=settings.redis.host,
            port=settings.redis.port,
        )
        with QuixStreamsStopUpdateStream(quix, city, sink) as stream:
            stream.run()
