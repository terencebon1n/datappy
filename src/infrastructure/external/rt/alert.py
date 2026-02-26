from typing import List

from google.transit import gtfs_realtime_pb2

from src.domain.gtfs_rt.alert import Alert, InformedEntity, Period


class AlertGateway:
    def _extract_text(self, translation_msg: gtfs_realtime_pb2.TranslatedString) -> str:
        if not translation_msg.translation:
            return ""
        return translation_msg.translation[0].text

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
                InformedEntity(route_id=ie.route_id, stop_id=ie.stop_id)
                for ie in alert.informed_entity
            ]

            alerts.append(
                Alert(
                    id=entity.id,
                    active_periods=periods,
                    informed_entities=entities,
                    header_text=self._extract_text(alert.header_text),
                    description_text=self._extract_text(alert.description_text),
                )
            )
        return alerts
