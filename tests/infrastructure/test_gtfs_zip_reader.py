import io
import zipfile
from unittest.mock import MagicMock, patch

import backend.infrastructure.external.gtfs_zip_reader as reader_module
from backend.domain.gtfs.enums import GTFSFileNames
from backend.infrastructure.external.gtfs_zip_reader import GTFSZipReader


def _zip_bytes() -> bytes:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as archive:
        archive.writestr(
            "agency.txt",
            "agency_id,agency_name,agency_timezone\n1,TAM,Europe/Paris\n",
        )
    return buffer.getvalue()


def _response() -> MagicMock:
    response = MagicMock()
    response.content = _zip_bytes()
    response.raise_for_status = MagicMock()
    return response


def test_reads_present_csv_and_reports_membership():
    with patch.object(reader_module.requests, "get", return_value=_response()):
        with GTFSZipReader("http://feed") as reader:
            assert reader.contains(GTFSFileNames.AGENCY) is True
            assert reader.contains(GTFSFileNames.STOPS) is False
            rows = list(reader.stream_csv(GTFSFileNames.AGENCY))

    assert rows == [
        {"agency_id": "1", "agency_name": "TAM", "agency_timezone": "Europe/Paris"}
    ]


def test_stream_csv_absent_file_yields_nothing():
    with patch.object(reader_module.requests, "get", return_value=_response()):
        with GTFSZipReader("http://feed") as reader:
            assert list(reader.stream_csv(GTFSFileNames.STOPS)) == []


def test_membership_and_stream_before_open():
    reader = GTFSZipReader("http://feed")  # never entered -> zip_file is None
    assert reader.contains(GTFSFileNames.AGENCY) is False
    assert list(reader.stream_csv(GTFSFileNames.AGENCY)) == []
    reader.__exit__(None, None, None)  # no zip_file -> no-op
