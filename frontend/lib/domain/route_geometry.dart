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

    const RouteStop({
        required this.id,
        required this.name,
        required this.latitude,
        required this.longitude,
    });
}

class RouteGeometry {
    final List<RouteShape> shapes;
    final List<RouteStop> stops;

    const RouteGeometry({required this.shapes, required this.stops});

    bool get isEmpty => shapes.isEmpty && stops.isEmpty;
}
