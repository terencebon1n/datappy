from typing import List, Optional

import httpx
from google.transit import gtfs_realtime_pb2

from backend.domain.gtfs_rt.alert import Alert, InformedEntity, Period
from backend.domain.gtfs_rt.enums import AlertCause, AlertEffect, AlertSeverity


class AlertGateway:
    async def fetch_rt(self, url: str) -> bytes:
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            response.raise_for_status()
            return response.content

    def _extract_text(self, translation_msg: gtfs_realtime_pb2.TranslatedString) -> str:
        if not translation_msg.translation:
            return ""
        return translation_msg.translation[0].text

    def _optional_field(
        self, message: gtfs_realtime_pb2.EntitySelector, field: str
    ) -> Optional[int]:
        if not message.HasField(field):
            return None
        return getattr(message, field)

    def _parse_informed_entity(
        self, selector: gtfs_realtime_pb2.EntitySelector
    ) -> InformedEntity:
        return InformedEntity(
            agency_id=selector.agency_id,
            route_id=selector.route_id,
            route_type=self._optional_field(selector, "route_type"),
            direction_id=self._optional_field(selector, "direction_id"),
            stop_id=selector.stop_id,
        )

    def parse_feed(self, payload: bytes) -> List[Alert]:
        feed = gtfs_realtime_pb2.FeedMessage()
        feed.ParseFromString(payload)

        alerts = []
        for entity in feed.entity:
            if not entity.HasField("alert"):
                continue

            alert = entity.alert

            periods = [
                Period(start=period.start, end=period.end)
                for period in alert.active_period
            ]

            entities = [
                self._parse_informed_entity(selector)
                for selector in alert.informed_entity
            ]

            alerts.append(
                Alert(
                    id=entity.id,
                    active_periods=periods,
                    informed_entities=entities,
                    cause=AlertCause(gtfs_realtime_pb2.Alert.Cause.Name(alert.cause)),
                    effect=AlertEffect(
                        gtfs_realtime_pb2.Alert.Effect.Name(alert.effect)
                    ),
                    severity=AlertSeverity(
                        gtfs_realtime_pb2.Alert.SeverityLevel.Name(alert.severity_level)
                    ),
                    header_text=self._extract_text(alert.header_text),
                    description_text=self._extract_text(alert.description_text),
                    url=self._extract_text(alert.url),
                )
            )
        return alerts
