from pyspark.sql import DataFrame, SparkSession

from src.infrastructure.config import AppConfig


class SparkConsumerAdapter:
    def __init__(self, appname: str) -> None:
        self.config = AppConfig.from_yaml("config.yaml")

        self.spark = (
            SparkSession.builder.remote("sc://localhost:15002")
            .appName(appname)
            .getOrCreate()
        )

        self.spark.conf.set("spark.sql.shuffle.partitions", "4")
        self.spark.conf.set("spark.sql.session.timeZone", "UTC")

    def stream(self, topic: str) -> DataFrame:
        return (
            self.spark.readStream.format("kafka")
            .options(**self.config.kafka.to_spark_options())
            .option("subscribe", topic)
            .option("failOnDataLoss", "false")
            .load()
        )
