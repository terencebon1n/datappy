import 'package:frontend/domain/coordinates.dart' show Coordinates;
import 'package:frontend/domain/route_geometry.dart'
    show RouteGeometry, RouteShape, RouteStop;


class RouteGeometryResponse {
    final List<RouteShape> shapes;
    final List<RouteStop> stops;

    RouteGeometryResponse({required this.shapes, required this.stops});

    factory RouteGeometryResponse.fromJson(Map<String, dynamic> json) {
        final shapes = (json['shapes'] as List?) ?? const [];
        final stops = (json['stops'] as List?) ?? const [];

        return RouteGeometryResponse(
            shapes: shapes
                .map((shape) => RouteShape(
                    directionId: (shape['direction_id'] as num).toInt(),
                    points: (((shape['points'] as List?) ?? const [])
                        .map((point) => Coordinates(
                            latitude: (point['latitude'] as num).toDouble(),
                            longitude: (point['longitude'] as num).toDouble(),
                        ))
                        .toList()),
                ))
                .toList(),
            stops: stops
                .map((stop) => RouteStop(
                    id: stop['id'] as String,
                    name: stop['name'] as String,
                    latitude: (stop['latitude'] as num).toDouble(),
                    longitude: (stop['longitude'] as num).toDouble(),
                ))
                .toList(),
        );
    }

    RouteGeometry toDomain() => RouteGeometry(shapes: shapes, stops: stops);
}
