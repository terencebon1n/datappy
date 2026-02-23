from dataclasses import dataclass
from typing import List, Optional, Type

from src.domain.gtfs_rt.enums import (
    AlertUrl,
    City,
    FeedType,
    TripUpdateUrl,
    VehiclePositionUrl,
)


@dataclass(frozen=True)
class ProducerTask:
    city: City
    feed_type: FeedType
    url: AlertUrl | TripUpdateUrl | VehiclePositionUrl


class ProducerRegistry:
    _URL_MAPPING: dict[FeedType, Type] = {
        FeedType.ALERT: AlertUrl,
        FeedType.TRIP_UPDATE: TripUpdateUrl,
        FeedType.VEHICLE_POSITION: VehiclePositionUrl,
    }

    @classmethod
    def get_all_tasks(cls) -> List[ProducerTask]:
        tasks = []
        for city in City:
            for feed in FeedType:
                url_enum = cls._URL_MAPPING.get(feed)
                if url_enum and hasattr(url_enum, city.name):
                    tasks.append(
                        ProducerTask(
                            city=city,
                            feed_type=feed,
                            url=getattr(url_enum, city.name).value,
                        )
                    )
        return tasks

    @classmethod
    def get_tasks(
        cls, city: Optional[City] = None, feed: Optional[FeedType] = None
    ) -> List[ProducerTask]:
        all_tasks = cls.get_all_tasks()
        if city:
            all_tasks = [t for t in all_tasks if t.city == city]
        if feed:
            all_tasks = [t for t in all_tasks if t.feed_type == feed]
        return all_tasks
