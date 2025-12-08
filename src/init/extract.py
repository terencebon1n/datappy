import csv
import io
import zipfile

import requests
from sqlalchemy.orm import Session

from ..dto.agency import AgencyContainer
from ..dto.calendar_date import CalendarDateContainer
from ..dto.route import RouteContainer
from ..dto.stop import StopContainer
from ..dto.stop_time import StopTimeContainer
from ..dto.transfer import TransferContainer
from ..dto.trip import TripContainer
from .enums.file_names import FileNames


def extract(url: str, session: Session) -> None:
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()

        zip_content = io.BytesIO(response.content)
    except requests.exceptions.RequestException as e:
        print(f"Error downloading file: {e}")
        return

    try:
        with zipfile.ZipFile(zip_content, "r") as zip_ref:
            file_names = sorted(zip_ref.namelist())
            if file_names != sorted(FileNames):
                raise ValueError("Zip file contains unexpected file names")
            for file_name in FileNames:
                with zip_ref.open(file_name, mode="r") as file:
                    text_file = io.TextIOWrapper(file, encoding="utf-8")
                    file_data = csv.DictReader(
                        text_file, delimiter=",", skipinitialspace=True
                    )
                    match file_name:
                        case FileNames.AGENCY:
                            agency_container = AgencyContainer()
                            agency_container.extract(file_data)
                            agency_container.load(session)
                        case FileNames.CALENDAR_DATE:
                            calendar_date_container = CalendarDateContainer()
                            calendar_date_container.extract(file_data)
                            calendar_date_container.load(session)
                        case FileNames.ROUTE:
                            route_container = RouteContainer()
                            route_container.extract(file_data)
                            route_container.load(session)
                        case FileNames.STOP:
                            stop_container = StopContainer()
                            stop_container.extract(file_data)
                            stop_container.load(session)
                        case FileNames.STOP_TIME:
                            stop_time_container = StopTimeContainer()
                            stop_time_container.extract(file_data)
                            stop_time_container.load(session)
                        case FileNames.TRANSFER:
                            transfer_container = TransferContainer()
                            transfer_container.extract(file_data)
                            transfer_container.load(session)
                        case FileNames.TRIP:
                            trip_container = TripContainer()
                            trip_container.extract(file_data)
                            trip_container.load(session)
    except Exception:
        raise Exception
