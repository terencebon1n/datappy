from quixstreams import Application
from quixstreams.dataframe import StreamingDataFrame
from quixstreams.models import Topic

from src.infrastructure.config import settings


class QuixStreamsConsumerAdapter:
    def __init__(self) -> None:
        self.app = Application(broker_address=settings.kafka.brokers)

    def stream(self, topic: str) -> StreamingDataFrame:
        input_topic: Topic = self.app.topic(topic)

        return self.app.dataframe(input_topic)
