from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from src.domain.gtfs.shape import Shape
from src.infrastructure.database.postgres.models.shape import ShapeModel
from src.infrastructure.database.repository import BaseRepository


class ShapeRepository(BaseRepository[Shape, ShapeModel]):
    domain = Shape
    model = ShapeModel

    def __init__(self, session: Session | AsyncSession) -> None:
        super().__init__(session)
