from aiokafka.admin import AIOKafkaAdminClient, NewTopic
from src.config import settings
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s:\t  %(message)s",
)

logger = logging.getLogger(__name__)


class KafkaAdminTool:
    def __init__(self):
        self.client = AIOKafkaAdminClient(bootstrap_servers=settings.kafka.brokers)

    async def ensure_topics(self, topic_names: list[str]):
        await self.client.start()
        try:
            existing_topics = await self.client.list_topics()
            new_topics = []

            for name in topic_names:
                if name not in existing_topics:
                    new_topics.append(
                        NewTopic(
                            name=name,
                            num_partitions=1,
                            replication_factor=1,
                            topic_configs={"cleanup.policy": "compact"},
                        )
                    )

            if new_topics:
                await self.client.create_topics(new_topics=new_topics)
                logger.info(
                    f"✅ Created new Kafka topics: {[t.name for t in new_topics]}"
                )
        finally:
            await self.client.close()
