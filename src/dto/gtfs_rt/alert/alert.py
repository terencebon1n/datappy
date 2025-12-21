from dataclasses import dataclass

import requests

from ..gtfs_rt_base import GTFSRTContainerBase, GTFSRTProducerBase
from ..period import Period
from .description import Description
from .header import Header
from .informed_entity import InformedEntity


@dataclass(frozen=True)
class Alert:
    id: str
    active_period: Period
    informed_entity: InformedEntity
    header: Header
    description: Description


class AlertEventProducer(GTFSRTProducerBase[Alert]):
    def __init__(self) -> None:
        super().__init__()

    async def send_dataclass(self, event: Alert):
        await self.producer.send(
            topic=self._resolve_dataclass_type.__name__,
            key=f"{event.informed_entity.route_id}".encode("utf-8"),
            value=self.encoder.encode(event),
        )


class AlertContainer(GTFSRTContainerBase[Alert]):
    items: list[Alert]

    def __init__(self) -> None:
        super().__init__()

    async def extract(self, url: str) -> list[Alert]:
        response = requests.get(url)
        self.feed.ParseFromString(response.content)
        for entity in self.feed.entity:
            self.items.append(
                Alert(
                    id=entity.id,
                    active_period=Period(
                        start=entity.alert.active_period[0].start,
                        end=entity.alert.active_period[0].end,
                    ),
                    informed_entity=InformedEntity(
                        route_id=entity.alert.informed_entity[0].route_id
                    ),
                    header=Header(text=entity.alert.header_text.translation[0].text),
                    description=Description(
                        text=entity.alert.description_text.translation[0].text
                    ),
                )
            )
        return self.items
