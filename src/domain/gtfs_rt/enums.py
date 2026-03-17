from enum import StrEnum


class FeedType(StrEnum):
    TRIP_UPDATE = "TripUpdate"
    VEHICLE_POSITION = "VehiclePosition"
    ALERT = "Alert"


class City(StrEnum):
    MONTPELLIER = "montpellier"
    BORDEAUX = "bordeaux"
    TOULOUSE = "toulouse"


class AlertUrl(StrEnum):
    MONTPELLIER = "https://gtfsproxy.e-tam.fr/URB/Alert.pb"
    BORDEAUX = "https://bdx.mecatran.com/utw/ws/gtfsfeed/alerts/bordeaux?apiKey=opendata-bordeaux-metropole-flux-gtfs-rt"
    TOULOUSE = "https://api.tisseo.fr/opendata/gtfsrt/GtfsRt.pb"


class TripUpdateUrl(StrEnum):
    MONTPELLIER = "https://gtfsproxy.e-tam.fr/URB/TripUpdate.pb"
    BORDEAUX = "https://bdx.mecatran.com/utw/ws/gtfsfeed/realtime/bordeaux?apiKey=opendata-bordeaux-metropole-flux-gtfs-rt"
    TOULOUSE = "https://api.tisseo.fr/opendata/gtfsrt/GtfsRt.pb"


class VehiclePositionUrl(StrEnum):
    MONTPELLIER = "https://gtfsproxy.e-tam.fr/URB/VehiclePosition.pb"
    BORDEAUX = "https://bdx.mecatran.com/utw/ws/gtfsfeed/vehicles/bordeaux?apiKey=opendata-bordeaux-metropole-flux-gtfs-rt"
    TOULOUSE = "https://api.tisseo.fr/opendata/gtfsrt/GtfsRt.pb"
