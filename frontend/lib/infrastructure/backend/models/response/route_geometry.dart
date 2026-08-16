import 'package:frontend/domain/coordinates.dart' show Coordinates;
import 'package:frontend/domain/route_geometry.dart'
    show RouteGeometry, RouteShape, RouteStop;


class RouteGeometryResponse {
    final List<RouteShape> shapes;
    final List<RouteStop> stops;
    final Map<int, String> directionHeadsigns;

    RouteGeometryResponse({
        required this.shapes,
        required this.stops,
        this.directionHeadsigns = const {},
    });

    factory RouteGeometryResponse.fromJson(Map<String, dynamic> json) {
        final shapes = (json['shapes'] as List?) ?? const [];
        final stops = (json['stops'] as List?) ?? const [];
        final headsigns = (json['direction_headsigns'] as List?) ?? const [];

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
                    code: stop['code'] as String?,
                    platformCode: stop['platform_code'] as String?,
                    wheelchairBoarding: (stop['wheelchair_boarding'] as num?)?.toInt(),
                ))
                .toList(),
            directionHeadsigns: {
                for (final entry in headsigns)
                    (entry['direction_id'] as num).toInt():
                        entry['headsign'] as String? ?? '',
            },
        );
    }

    RouteGeometry toDomain() => RouteGeometry(
        shapes: shapes,
        stops: stops,
        directionHeadsigns: directionHeadsigns,
    );
}
