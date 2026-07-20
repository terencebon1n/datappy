from datetime import datetime, timezone
from typing import List

from backend.application.dto.alert import AlertPathDTO
from backend.application.ports import AlertReader
from backend.domain.gtfs_rt.alert import Alert


class AlertFeedService:
    def __init__(self, alert_repository: AlertReader) -> None:
        self.alert_repository = alert_repository

    async def get_alerts(self, transit: AlertPathDTO) -> List[Alert]:
        now = int(datetime.now(tz=timezone.utc).timestamp())

        alerts = await self.alert_repository.get_alerts(transit.city)

        linked = [
            alert
            for alert in alerts
            if alert.is_active(now)
            and alert.concerns(transit.route_id, transit.direction_id, transit.stop_id)
        ]

        linked.sort(key=lambda alert: (alert.severity.rank, alert.id))

        return linked
