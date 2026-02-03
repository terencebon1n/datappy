from typing import Optional

from sqlalchemy.orm import Session

from src.domain.gtfs.agency import Agency
from src.infrastructure.database.postgres.models.agency import AgencyModel
from src.infrastructure.database.repository import BaseRepository


class AgencyRepository(BaseRepository[Agency, AgencyModel]):
    domain = Agency
    model = AgencyModel

    def __init__(self, session: Session) -> None:
        super().__init__(session)

    # You can add agency-specific queries here
    def get_by_name(self, name: str) -> Optional[Agency]:
        obj = self.session.query(self.model).filter(self.model.name == name).first()
        return Agency.model_validate(obj) if obj else None
