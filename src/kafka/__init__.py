import asyncio
import json
import time
import requests
from google.transit import gtfs_realtime_pb2
from aiokafka import AIOKafkaProducer
from ..config import settings


class Producer:
    def __init__(self) -> None:
        producer = AIOKafkaProducer(
            bootstrap_servers=settings.kafka.brokers, value_serializer=kafka_serde
        )

    def start(self) -> None:
        print("broker started")
