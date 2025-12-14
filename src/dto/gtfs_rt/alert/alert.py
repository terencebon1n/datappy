from dataclasses import dataclass

import requests

from ..gtfs_rt_base import GTFSRTContainerBase
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
                    id=entity.alert.id,
                    active_period=Period(
                        start=entity.alert.active_period.start,
                        end=entity.alert.active_period.end,
                    ),
                    informed_entity=InformedEntity(
                        route_id=entity.alert.informed_entity.route_id
                    ),
                    header=Header(text=entity.alert.header.text),
                    description=Description(text=entity.alert.description.text),
                )
            )
        return self.items
