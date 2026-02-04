from enum import StrEnum


class FeedType(StrEnum):
    TRIP_UPDATE = "TripUpdate"
    VEHICLE_POSITION = "VehiclePosition"
    ALERT = "Alert"


class City(StrEnum):
    MONTPELLIER = "montpellier"


class AlertUrl(StrEnum):
    MONTPELLIER = "https://gtfsproxy.e-tam.fr/URB/Alert.pb"


class TripUpdateUrl(StrEnum):
    MONTPELLIER = "https://gtfsproxy.e-tam.fr/URB/TripUpdate.pb"


class VehiclePositionUrl(StrEnum):
    MONTPELLIER = "https://gtfsproxy.e-tam.fr/URB/VehiclePosition.pb"
