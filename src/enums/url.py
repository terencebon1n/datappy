from enum import StrEnum


class TAM_MMM_GTFS_RT(StrEnum):
    TRIP_UPDATE = "https://data.montpellier3m.fr/GTFS/Urbain/TripUpdate.pb"
    VEHICLE_POSITION = "https://data.montpellier3m.fr/GTFS/Urbain/VehiclePosition.pb"
    ALERT = "https://data.montpellier3m.fr/GTFS/Urbain/Alert.pb"
    GTFS_ZIP = "https://data.montpellier3m.fr/GTFS/Urbain/GTFS.zip"
