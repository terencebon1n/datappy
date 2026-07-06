from enum import StrEnum


class GTFSFileNames(StrEnum):
    AGENCY = "agency.txt"
    CALENDAR = "calendar.txt"
    CALENDAR_DATES = "calendar_dates.txt"
    FEED_INFO = "feed_info.txt"
    ROUTES = "routes.txt"
    SHAPES = "shapes.txt"
    STOPS = "stops.txt"
    STOP_TIMES = "stop_times.txt"
    TRANSFERS = "transfers.txt"
    TRIPS = "trips.txt"
