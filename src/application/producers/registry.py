from dataclasses import dataclass
from typing import List, Optional

from src.domain.gtfs_rt.enums import City, FeedType
from src.infrastructure.config import CityFeedsModel, settings


@dataclass(frozen=True)
class ProducerTask:
    city: City
    feed_type: FeedType
    url: str


class ProducerRegistry:
    @staticmethod
    def _url_for(feeds: CityFeedsModel, feed_type: FeedType) -> Optional[str]:
        match feed_type:
            case FeedType.ALERT:
                return feeds.alert
            case FeedType.TRIP_UPDATE:
                return feeds.trip_update
            case FeedType.VEHICLE_POSITION:
                return feeds.vehicle_position

    @classmethod
    def get_all_tasks(cls) -> List[ProducerTask]:
        tasks = []
        for city, feeds in settings.feeds.items():
            for feed_type in FeedType:
                url = cls._url_for(feeds, feed_type)
                if url:
                    tasks.append(ProducerTask(city=city, feed_type=feed_type, url=url))
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
