from sqlalchemy.schema import CreateSchema

from backend.application.services.populate.gtfs_loader import GTFSLoaderService
from backend.domain.gtfs_rt.enums import City
from backend.infrastructure.config import settings
from backend.infrastructure.database.postgres.base import GTFSModelBase
from backend.infrastructure.database.postgres.manager import PostgresDatabaseManager
from backend.infrastructure.external.gtfs_zip_reader import GTFSZipReader


class PopulateService:
    async def start(self, city: City) -> None:
        feeds = settings.feeds.get(city)
        if feeds is None:
            raise ValueError(f"No feed configuration for city: {city}")

        db_manager = PostgresDatabaseManager(is_async=False)
        db_manager.initialize()
        db_manager.set_schema(city)

        GTFSModelBase.metadata.drop_all(db_manager.engine)

        db_manager.session.execute(CreateSchema(name=city, if_not_exists=True))
        db_manager.session.commit()

        GTFSModelBase.metadata.create_all(db_manager.engine)

        with GTFSZipReader(feeds.gtfs_schedule) as source:
            GTFSLoaderService(db_manager.session, source, city).perform_import()

        await db_manager.close()
