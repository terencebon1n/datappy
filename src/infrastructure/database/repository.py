import logging
from itertools import islice
from typing import Iterable

from pydantic import BaseModel
from sqlalchemy import Result, Select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from .postgres.base import GTFSModelBase

logger = logging.getLogger(__name__)


class AsyncQueryRepository[TModel: GTFSModelBase]:
    model: type[TModel]

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def execute_select(self, select_query: Select) -> Result:
        return await self.session.execute(select_query)


class BulkIngestRepository:
    def __init__(
        self,
        session: Session,
        domain: type[BaseModel],
        model: type[GTFSModelBase],
    ) -> None:
        self.session = session
        self.domain = domain
        self.model = model

    def bulk_add(self, rows: Iterable[dict], batch_size: int = 2000) -> None:
        iterator = iter(rows)
        total = 0
        while True:
            batch_raw = list(islice(iterator, batch_size))
            if not batch_raw:
                break
            mappings = []
            for row in batch_raw:
                try:
                    domain = self.domain(**row)
                except Exception:
                    logger.error(f"Invalid row for {self.model.__tablename__}: {row}")
                    raise
                mappings.append(domain.model_dump())

            self.session.execute(
                insert(self.model).values(mappings).on_conflict_do_nothing()
            )

            total += len(mappings)
            logger.info(f"Inserted {total} rows into {self.model.__tablename__}")
