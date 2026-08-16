import 'package:frontend/domain/coordinates.dart' show Coordinates;


class RouteShape {
    final int directionId;
    final List<Coordinates> points;

    const RouteShape({required this.directionId, required this.points});
}

class RouteStop {
    final String id;
    final String name;
    final double latitude;
    final double longitude;
    final String? code;
    final String? platformCode;
    final int? wheelchairBoarding;

    const RouteStop({
        required this.id,
        required this.name,
        required this.latitude,
        required this.longitude,
        this.code,
        this.platformCode,
        this.wheelchairBoarding,
    });

    bool get isWheelchairAccessible => wheelchairBoarding == 1;

    bool get isWheelchairInaccessible => wheelchairBoarding == 2;
}

class RouteGeometry {
    final List<RouteShape> shapes;
    final List<RouteStop> stops;
    final Map<int, String> directionHeadsigns;

    const RouteGeometry({
        required this.shapes,
        required this.stops,
        this.directionHeadsigns = const {},
    });

    bool get isEmpty => shapes.isEmpty && stops.isEmpty;

    String? headsignFor(int directionId) => directionHeadsigns[directionId];
}
