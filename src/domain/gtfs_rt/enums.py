from enum import StrEnum


class FeedType(StrEnum):
    TRIP_UPDATE = "TripUpdate"
    VEHICLE_POSITION = "VehiclePosition"
    ALERT = "Alert"


class City(StrEnum):
    MONTPELLIER = "montpellier"
    BORDEAUX = "bordeaux"
    TOULOUSE = "toulouse"
