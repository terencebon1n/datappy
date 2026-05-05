from diagrams import Cluster, Diagram
from diagrams.custom import Custom
from diagrams.onprem.database import PostgreSQL
from diagrams.onprem.inmemory import Redis
from diagrams.onprem.queue import Kafka
from diagrams.programming.framework import FastAPI
from diagrams.programming.language import Python


class DiagramService:
    def start(self) -> None:
        with Diagram("Datappy", show=False, outformat="png"):
            with Cluster("External Data Sources"):
                source_rt = Custom(
                    "GTFS Realtime", "src/application/services/diagram/gtfs_rt.png"
                )
                source_schedule = Custom(
                    "GTFS Schedule",
                    "src/application/services/diagram/gtfs_schedule.png",
                )

            with Cluster("Datappy Environment (Docker Compose)"):
                populate = Python("populate {city}")
                postgres_destination = PostgreSQL("Primary Database (PostgreSQL)")
                producer = Python("producer {city}")
                kafka_events = Kafka("Event Stream (Kafka)")
                consumer = Python("consumer {city}")
                redis_sink = Redis("Realtime State (Redis)")
                fastapi = FastAPI("Datappy Backend (FastAPI)")

            source_schedule >> populate >> postgres_destination >> fastapi

            source_rt >> producer >> kafka_events >> consumer >> redis_sink >> fastapi
