from contextlib import ExitStack

from backend.application.consumers.quixstreams.alert import QuixStreamsAlertStream
from backend.application.consumers.quixstreams.stop_update import (
    QuixStreamsStopUpdateStream,
)
from backend.application.consumers.quixstreams.vehicle_position import (
    QuixStreamsVehiclePositionStream,
)
from backend.domain.gtfs_rt.enums import City
from backend.infrastructure.config import settings
from backend.infrastructure.database.redis.sink import (
    RedisHsetAlertSink,
    RedisHsetStopUpdateSink,
    RedisHsetVehiclePositionSink,
)
from backend.infrastructure.processing.quixstreams.consumer import (
    QuixStreamsConsumerAdapter,
)


class QuixStreamsConsumerService:
    def start(self, city: City) -> None:
        quix = QuixStreamsConsumerAdapter(consumer_group=f"stop-update-{city}")
        stop_update_sink = RedisHsetStopUpdateSink(
            city=city,
            host=settings.redis.host,
            port=settings.redis.port,
        )
        alert_sink = RedisHsetAlertSink(
            city=city,
            host=settings.redis.host,
            port=settings.redis.port,
        )
        vehicle_position_sink = RedisHsetVehiclePositionSink(
            city=city,
            host=settings.redis.host,
            port=settings.redis.port,
        )
        with ExitStack() as stack:
            stream = stack.enter_context(
                QuixStreamsStopUpdateStream(quix, city, stop_update_sink)
            )
            stack.enter_context(QuixStreamsAlertStream(quix, city, alert_sink))
            stack.enter_context(
                QuixStreamsVehiclePositionStream(quix, city, vehicle_position_sink)
            )
            stream.run()
