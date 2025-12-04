from enum import StrEnum


class TAM_MMM_GTFS_RT(StrEnum):
    TRIP_UPDATE = "https://data.montpellier3m.fr/TAM_MMM_GTFSRT/TripUpdate.pb"
    VEHICLE_POSITION = "https://data.montpellier3m.fr/TAM_MMM_GTFSRT/VehiclePosition.pb"
    ALERT = "https://data.montpellier3m.fr/TAM_MMM_GTFSRT/Alert.pb"
    GTFS_ZIP = "https://data.montpellier3m.fr/TAM_MMM_GTFSRT/GTFS.zip"
