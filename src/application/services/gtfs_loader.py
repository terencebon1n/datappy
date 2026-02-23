from sqlalchemy.orm import Session

from src.domain.gtfs.enums import GTFSCityUrls
from src.infrastructure.database.postgres.repositories.registry import (
    RepositoryRegistry,
)
from src.infrastructure.external.gtfs_zip_reader import GTFSZipReader


class GTFSLoaderService:
    def __init__(self, session: Session):
        self.session = session

    def perform_import(self, url: GTFSCityUrls):
        with GTFSZipReader(url) as reader:
            for file_type in RepositoryRegistry.supported_files():
                # Check if the file exists in the ZIP
                if not reader.zip_file or file_type not in reader.zip_file.namelist():
                    continue

                # Get the initialized repository from the Registry
                repository = RepositoryRegistry.get_repository_for_file(
                    file_type, self.session
                )

                # Stream and process
                raw_rows = reader.stream_csv(file_type)
                repository.bulk_add(raw_rows)
