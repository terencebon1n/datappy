import logging
from itertools import islice
from typing import Iterable, Type, TypeVar

from pydantic import BaseModel
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from .postgres.base import GTFSModelBase

TDomain = TypeVar("TDomain", bound=BaseModel)
TModel = TypeVar("TModel", bound=GTFSModelBase)


logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s:\t  %(message)s",
)

logger = logging.getLogger(__name__)


class BaseRepository[TDomain, TModel]:
    domain: Type[TDomain]
    model: Type[TModel]

    def __init__(
        self,
        session: Session,
    ) -> None:
        self.session = session

    def bulk_add(self, generator: Iterable[dict], batch_size: int = 5000) -> None:
        i = 0
        while True:
            batch_raw = list(islice(generator, batch_size))
            if not batch_raw:
                break

            batch_domain = [self.domain(**row) for row in batch_raw]
            mappings = [obj.model_dump() for obj in batch_domain]

            self.session.execute(
                insert(self.model).values(mappings).on_conflict_do_nothing()
            )
            self.session.commit()

            logger.info(
                f"Inserted {(i * batch_size) + len(mappings)} rows into {self.model.__tablename__}"
            )

            i += 1
