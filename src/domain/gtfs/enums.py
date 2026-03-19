from enum import StrEnum


class GTFSFileNames(StrEnum):
    AGENCY = "agency.txt"
    CALENDAR = "calendar.txt"
    CALENDAR_DATES = "calendar_dates.txt"
    ROUTES = "routes.txt"
    SHAPES = "shapes.txt"
    STOPS = "stops.txt"
    STOP_TIMES = "stop_times.txt"
    TRANSFERS = "transfers.txt"
    TRIPS = "trips.txt"


class GTFSCityUrls(StrEnum):
    MONTPELLIER = "https://gtfsproxy.e-tam.fr/URB/GTFS.zip"
    BORDEAUX = "https://bdx.mecatran.com/utw/ws/gtfsfeed/static/bordeaux?apiKey=opendata-bordeaux-metropole-flux-gtfs-rt"
    TOULOUSE = "https://data.toulouse-metropole.fr/explore/dataset/tisseo-gtfs/files/fc1dda89077cf37e4f7521760e0ef4e9/download/"
