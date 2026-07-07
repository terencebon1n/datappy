from backend.domain.admin.process import ManagedServiceType, ProcessStatus
from backend.domain.enums import RouteTypeId, RouteTypeName
from backend.domain.gtfs.enums import GTFSFileNames
from backend.domain.gtfs_rt.enums import City, FeedType


def test_route_type_id_values():
    assert RouteTypeId.TRAM == 0
    assert RouteTypeId.FUNICULAR == 7
    assert [t.value for t in RouteTypeId] == [0, 1, 2, 3, 4, 5, 6, 7]


def test_route_type_name_values():
    assert RouteTypeName.BUS == "Bus"
    assert RouteTypeName.CABLE_CAR == "Cable Car"
    assert len(list(RouteTypeName)) == 8


def test_gtfs_file_names():
    assert GTFSFileNames.STOPS == "stops.txt"
    assert GTFSFileNames.TRIPS.value == "trips.txt"
    assert len(list(GTFSFileNames)) == 10


def test_city_enum():
    assert City.MONTPELLIER == "montpellier"
    assert set(City) == {
        City.MONTPELLIER,
        City.BORDEAUX,
        City.TOULOUSE,
        City.NIMES,
    }


def test_feed_type_topic_for_every_type_and_city():
    assert FeedType.TRIP_UPDATE.topic(City.MONTPELLIER) == "montpellier.TripUpdate"
    assert FeedType.VEHICLE_POSITION.topic(City.BORDEAUX) == "bordeaux.VehiclePosition"
    assert FeedType.ALERT.topic(City.NIMES) == "nimes.Alert"


def test_admin_enums():
    assert ManagedServiceType.PRODUCER == "producer"
    assert ManagedServiceType.CONSUMER == "consumer"
    assert {s.value for s in ProcessStatus} == {"running", "stopped", "crashed"}
