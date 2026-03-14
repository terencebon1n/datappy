from src.application.consumers.stop_update import StopUpdateStream
from src.infrastructure.database.redis.sink.stop_update import StopUpdateSink
from src.infrastructure.processing.spark.consumer import SparkConsumerAdapter


class ConsumerService:
    def start(self) -> None:
        spark = SparkConsumerAdapter("StopUpdateStream")
        sink = StopUpdateSink()
        with StopUpdateStream(spark, sink) as stream:
            stream.awaitTermination()
