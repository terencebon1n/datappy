from ..enums.url import TAM_MMM_GTFS_RT
from .extract import extract


class Init:
    def start(self) -> None:
        extract(TAM_MMM_GTFS_RT.GTFS_ZIP)
