from unittest.mock import MagicMock

import backend.application.services.populate.gtfs_loader as loader_module
from backend.application.services.populate.gtfs_loader import GTFSLoaderService
from backend.domain.gtfs.enums import GTFSFileNames
from backend.domain.gtfs_rt.enums import City


def test_perform_import_processes_present_files_and_skips_absent(monkeypatch):
    repo = MagicMock()
    fake_registry = MagicMock()
    fake_registry.supported_files.return_value = [
        GTFSFileNames.AGENCY,  # present -> defaults with agency_id
        GTFSFileNames.STOPS,  # present -> no defaults
        GTFSFileNames.TRIPS,  # absent -> skipped
    ]
    fake_registry.get_repository_for_file.return_value = repo
    monkeypatch.setattr(loader_module, "RepositoryRegistry", fake_registry)

    source = MagicMock()
    source.contains.side_effect = lambda f: f != GTFSFileNames.TRIPS
    source.stream_csv.return_value = iter([{"a": 1}])
    session = MagicMock()

    service = GTFSLoaderService(session, source, City.MONTPELLIER)
    service.perform_import()

    assert repo.bulk_add.call_count == 2  # AGENCY + STOPS, not TRIPS
    agency_call = repo.bulk_add.call_args_list[0]
    stops_call = repo.bulk_add.call_args_list[1]
    assert agency_call.kwargs["defaults"] == {"agency_id": "montpellier"}
    assert stops_call.kwargs["defaults"] is None
    assert session.commit.call_count == 2


def test_defaults_for():
    service = GTFSLoaderService(MagicMock(), MagicMock(), City.NIMES)
    assert service._defaults_for(GTFSFileNames.AGENCY) == {"agency_id": "nimes"}
    assert service._defaults_for(GTFSFileNames.STOPS) is None
