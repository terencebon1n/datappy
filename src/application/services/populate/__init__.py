from sqlalchemy.schema import CreateSchema

from src.application.services.populate.gtfs_loader import GTFSLoaderService
from src.domain.gtfs.enums import GTFSCityUrls
from src.domain.gtfs_rt.enums import City
from src.infrastructure.database.postgres.base import GTFSModelBase
from src.infrastructure.database.postgres.manager import PostgresDatabaseManager


class PopulateService:
    async def start(self, city: City) -> None:
        db_manager = PostgresDatabaseManager(is_async=False)
        db_manager.initialize()
        db_manager.set_schema(city)

        GTFSModelBase.metadata.drop_all(db_manager.engine)

        db_manager.session.execute(CreateSchema(name=city, if_not_exists=True))
        db_manager.session.commit()

        GTFSModelBase.metadata.create_all(db_manager.engine)

        gtfs_loader = GTFSLoaderService(db_manager.session)
        gtfs_loader.perform_import(GTFSCityUrls[city.name])

        await db_manager.close()
