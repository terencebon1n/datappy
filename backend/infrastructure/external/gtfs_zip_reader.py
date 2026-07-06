from __future__ import annotations

import csv
import io
import zipfile
from types import TracebackType
from typing import Generator, Optional, Type

import requests

from backend.domain.gtfs.enums import GTFSFileNames


class GTFSZipReader:
    def __init__(self, url: str) -> None:
        self.url = url
        self.zip_file: zipfile.ZipFile | None = None

    def __enter__(self) -> GTFSZipReader:
        response = requests.get(self.url, stream=True)
        response.raise_for_status()

        self.zip_file = zipfile.ZipFile(io.BytesIO(response.content))
        return self

    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_value: Optional[BaseException],
        traceback: Optional[TracebackType],
    ) -> None:
        if self.zip_file:
            self.zip_file.close()

    def contains(self, filename: GTFSFileNames) -> bool:
        return self.zip_file is not None and filename in self.zip_file.namelist()

    def stream_csv(self, filename: GTFSFileNames) -> Generator[dict, None, None]:
        """Streams rows from a specific CSV inside the ZIP as dictionaries."""
        if not self.zip_file or filename not in self.zip_file.namelist():
            return

        with self.zip_file.open(filename, "r") as file:
            text_file = io.TextIOWrapper(file, encoding="utf-8-sig")
            reader = csv.DictReader(text_file, delimiter=",", skipinitialspace=True)
            for row in reader:
                yield row
