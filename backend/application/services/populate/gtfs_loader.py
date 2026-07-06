from sqlalchemy.orm import Session

from backend.application.ports import GTFSScheduleSource
from backend.domain.gtfs.enums import GTFSFileNames
from backend.domain.gtfs_rt.enums import City
from backend.infrastructure.database.postgres.repositories.registry import (
    RepositoryRegistry,
)


class GTFSLoaderService:
    def __init__(
        self, session: Session, source: GTFSScheduleSource, city: City
    ) -> None:
        self.session = session
        self.source = source
        self.city = city

    def perform_import(self) -> None:
        for file_type in RepositoryRegistry.supported_files():
            if not self.source.contains(file_type):
                continue

            repository = RepositoryRegistry.get_repository_for_file(
                file_type, self.session
            )

            raw_rows = self.source.stream_csv(file_type)
            repository.bulk_add(raw_rows, defaults=self._defaults_for(file_type))
            self.session.commit()

    def _defaults_for(self, file_type: GTFSFileNames) -> dict | None:
        if file_type == GTFSFileNames.AGENCY:
            return {"agency_id": str(self.city)}
        return None
