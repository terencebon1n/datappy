from quixstreams import Application
from quixstreams.dataframe import StreamingDataFrame
from quixstreams.models import Topic
from quixstreams.sinks.community.redis import RedisSink


class QuixStreamsConsumerAdapter:
    def __init__(self) -> None:
        self.app = Application(broker_address="localhost:9092")
        self.redis_sink = RedisSink(
            host="localhost",
            port=6379,
            db=0,
        )

    def stream(self, topic: str) -> StreamingDataFrame:
        input_topic: Topic = self.app.topic(topic)

        return self.app.dataframe(input_topic)

    def sink(self, sdf: StreamingDataFrame) -> None:
        sdf.sink(self.redis_sink)
