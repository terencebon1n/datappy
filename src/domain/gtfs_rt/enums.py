from enum import StrEnum


class City(StrEnum):
    MONTPELLIER = "montpellier"
    BORDEAUX = "bordeaux"
    TOULOUSE = "toulouse"
    NIMES = "nimes"


class FeedType(StrEnum):
    TRIP_UPDATE = "TripUpdate"
    VEHICLE_POSITION = "VehiclePosition"
    ALERT = "Alert"

    def topic(self, city: City) -> str:
        return f"{city}.{self.value}"
