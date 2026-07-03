from sqlalchemy.orm import Session

from src.application.ports import GTFSScheduleSource
from src.infrastructure.database.postgres.repositories.registry import (
    RepositoryRegistry,
)


class GTFSLoaderService:
    def __init__(self, session: Session, source: GTFSScheduleSource) -> None:
        self.session = session
        self.source = source

    def perform_import(self) -> None:
        for file_type in RepositoryRegistry.supported_files():
            if not self.source.contains(file_type):
                continue

            repository = RepositoryRegistry.get_repository_for_file(
                file_type, self.session
            )

            raw_rows = self.source.stream_csv(file_type)
            repository.bulk_add(raw_rows)
            self.session.commit()
