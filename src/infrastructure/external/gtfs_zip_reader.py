import csv
import io
import zipfile
from typing import Generator

import requests

from src.domain.gtfs.enums import GTFSCityUrls, GTFSFileNames


class GTFSZipReader:
    def __init__(self, url: GTFSCityUrls) -> None:
        self.url = url
        self.zip_file: zipfile.ZipFile | None = None

    def __enter__(self):
        response = requests.get(self.url, stream=True)
        response.raise_for_status()

        self.zip_file = zipfile.ZipFile(io.BytesIO(response.content))
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.zip_file:
            self.zip_file.close()

    def stream_csv(self, filename: GTFSFileNames) -> Generator[dict, None, None]:
        """Streams rows from a specific CSV inside the ZIP as dictionaries."""
        if not self.zip_file or filename not in self.zip_file.namelist():
            return

        with self.zip_file.open(filename, "r") as file:
            text_file = io.TextIOWrapper(file, encoding="utf-8-sig")
            reader = csv.DictReader(text_file, delimiter=",", skipinitialspace=True)
            for row in reader:
                yield row
