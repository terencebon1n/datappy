from sqlalchemy.orm import Session

from src.domain.gtfs.feed_info import FeedInfo
from src.infrastructure.database.postgres.models.feed_info import FeedInfoModel
from src.infrastructure.database.repository import BaseRepository


class FeedInfoRepository(BaseRepository[FeedInfo, FeedInfoModel]):
    domain = FeedInfo
    model = FeedInfoModel

    def __init__(self, session: Session) -> None:
        super().__init__(session)
