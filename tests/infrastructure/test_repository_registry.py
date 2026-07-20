from unittest.mock import MagicMock

import pytest

from backend.domain.gtfs.enums import GTFSFileNames
from backend.infrastructure.database.postgres.repositories.registry import (
    RepositoryRegistry,
)
from backend.infrastructure.database.repository import BulkIngestRepository


def test_supported_files_lists_all_ten():
    assert len(RepositoryRegistry.supported_files()) == 10
    assert GTFSFileNames.AGENCY in RepositoryRegistry.supported_files()


def test_get_repository_for_known_file():
    repo = RepositoryRegistry.get_repository_for_file(GTFSFileNames.AGENCY, MagicMock())
    assert isinstance(repo, BulkIngestRepository)


def test_get_repository_for_unknown_file_raises(monkeypatch):
    # Force a lookup miss to exercise the guard clause.
    monkeypatch.setattr(RepositoryRegistry, "_mapping", {})
    with pytest.raises(ValueError, match="No repository registered"):
        RepositoryRegistry.get_repository_for_file(GTFSFileNames.AGENCY, MagicMock())
