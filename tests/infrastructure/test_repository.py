from unittest.mock import AsyncMock, MagicMock

import pytest

from backend.domain.gtfs.agency import Agency
from backend.infrastructure.database.postgres.models.agency import AgencyModel
from backend.infrastructure.database.repository import (
    AsyncQueryRepository,
    BulkIngestRepository,
)


async def test_async_query_repository_execute_select():
    session = MagicMock()
    result = MagicMock()
    session.execute = AsyncMock(return_value=result)

    repo = AsyncQueryRepository(session)
    query = MagicMock()
    assert await repo.execute_select(query) is result
    session.execute.assert_awaited_once_with(query)


def _bulk_repo() -> tuple[BulkIngestRepository, MagicMock]:
    session = MagicMock()
    repo = BulkIngestRepository(session, domain=Agency, model=AgencyModel)
    return repo, session


def test_bulk_add_batches_and_applies_defaults():
    repo, session = _bulk_repo()
    rows = [
        {"agency_name": "TAM", "agency_timezone": "Europe/Paris"},
        {"agency_name": "TBM", "agency_timezone": "Europe/Paris"},
    ]
    repo.bulk_add(rows, batch_size=1, defaults={"agency_id": "montpellier"})
    # batch_size=1 -> two batches -> two INSERT executions
    assert session.execute.call_count == 2


def test_bulk_add_without_defaults():
    repo, session = _bulk_repo()
    repo.bulk_add(
        [{"agency_name": "TAM", "agency_timezone": "Europe/Paris"}], defaults=None
    )
    session.execute.assert_called_once()


def test_bulk_add_empty_is_noop():
    repo, session = _bulk_repo()
    repo.bulk_add([])
    session.execute.assert_not_called()


def test_bulk_add_invalid_row_raises():
    repo, session = _bulk_repo()
    with pytest.raises(Exception):
        repo.bulk_add([{"totally": "invalid"}])
    session.execute.assert_not_called()
