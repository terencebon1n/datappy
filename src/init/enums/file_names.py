from enum import StrEnum


class FileNames(StrEnum):
    CALENDAR_DATE = "calendar_dates.txt"
    AGENCY = "agency.txt"
    ROUTE = "routes.txt"
    STOP = "stops.txt"
    TRIP = "trips.txt"
    STOP_TIME = "stop_times.txt"
    TRANSFER = "transfers.txt"
