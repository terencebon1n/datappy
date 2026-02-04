from src.domain.gtfs_rt.trip_update import TripUpdate, MinimizedTripUpdate
from src.infrastructure.messaging.kafka_producer import KafkaProducerAdapter
from src.infrastructure.external.rt.trip_update import TripUpdateGateway
from src.application.producers.registry import ProducerTask


class TripIngestorService:
    def __init__(self, client: TripUpdateGateway, kafka_adapter: KafkaProducerAdapter):
        self.client = client
        self.kafka = kafka_adapter
        self.topic = "TripUpdate"

    async def run(self, task: ProducerTask):
        raw_data = await self.client.fetch_rt(task.url)
        trip_updates: list[TripUpdate] = self.client.parse_feed(raw_data)

        for event in trip_updates:
            for stop_time in event.stop_times:
                minimized = MinimizedTripUpdate(
                    id=event.id, trip=event.trip, stop_time=stop_time
                )

                key = f"{event.trip.route_id}_{event.trip.direction_id}_{stop_time.id}"

                await self.kafka.send(
                    topic=self.topic,
                    key=key,
                    value=minimized.model_dump_json().encode("utf-8"),
                )
