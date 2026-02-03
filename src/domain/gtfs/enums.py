from enum import StrEnum


class GTFSFileNames(StrEnum):
    AGENCY = "agency.txt"
    CALENDAR_DATES = "calendar_dates.txt"
    ROUTES = "routes.txt"
    STOPS = "stops.txt"
    STOP_TIMES = "stop_times.txt"
    TRANSFERS = "transfers.txt"
    TRIPS = "trips.txt"


class GTFSCityUrls(StrEnum):
    MONTPELLIER = "https://gtfsproxy.e-tam.fr/URB/GTFS.zip"
