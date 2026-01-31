from enum import StrEnum


class TAM_MMM_GTFS_RT(StrEnum):
    TRIP_UPDATE = "https://gtfsproxy.e-tam.fr/URB/TripUpdate.pb"
    VEHICLE_POSITION = "https://gtfsproxy.e-tam.fr/URB/VehiclePosition.pb"
    ALERT = "https://gtfsproxy.e-tam.fr/URB/Alert.pb"
    GTFS_ZIP = "https://gtfsproxy.e-tam.fr/URB/GTFS.zip"
