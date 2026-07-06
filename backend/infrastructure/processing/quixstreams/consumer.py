from quixstreams import Application
from quixstreams.dataframe import StreamingDataFrame
from quixstreams.models import Topic

from backend.infrastructure.config import settings


class QuixStreamsConsumerAdapter:
    def __init__(self, consumer_group: str) -> None:
        self.app = Application(
            broker_address=settings.kafka.brokers,
            consumer_group=consumer_group,
        )

    def stream(self, topic: str) -> StreamingDataFrame:
        input_topic: Topic = self.app.topic(topic)

        return self.app.dataframe(input_topic)
