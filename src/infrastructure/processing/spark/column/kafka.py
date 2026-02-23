from ..base import SparkColumns


class KafkaColumns(SparkColumns):
    KEY = "key"
    VALUE = "value"
    TIMESTAMP = "timestamp"
