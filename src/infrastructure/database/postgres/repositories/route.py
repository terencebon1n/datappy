from sqlalchemy.orm import Session

from src.domain.gtfs.route import Route
from src.infrastructure.database.postgres.models.route import RouteModel
from src.infrastructure.database.repository import BaseRepository


class RouteRepository(BaseRepository[Route, RouteModel]):
    domain = Route
    model = RouteModel

    def __init__(self, session: Session) -> None:
        super().__init__(session)
