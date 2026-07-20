import json
import logging
from typing import List

from redis import Redis

from backend.domain.gtfs_rt.alert import Alert
from backend.domain.gtfs_rt.enums import City
from backend.infrastructure.database.redis.sink.alert import alert_key

logger = logging.getLogger(__name__)


class AlertRepository:
    def __init__(self, redis: Redis) -> None:
        self.redis = redis

    async def get_alerts(self, city: City) -> List[Alert]:
        key = alert_key(city)

        data = self.redis.hgetall(key)

        if not data:
            return []

        alerts = []
        for value in data.values():
            try:
                payload = json.loads(value)
                alerts.append(
                    Alert.model_validate({**payload, "id": payload["alert_id"]})
                )
            except (json.JSONDecodeError, KeyError, ValueError) as e:
                logger.warning(f"Skipping malformed alert in {key}: {e}")
                continue
        return alerts
