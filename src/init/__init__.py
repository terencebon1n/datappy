from sqlalchemy.orm import Session

from ..enums.url import TAM_MMM_GTFS_RT
from .extract import extract


class Init:
    def load_gtfs(self, session: Session) -> None:
        extract(TAM_MMM_GTFS_RT.GTFS_ZIP, session)
