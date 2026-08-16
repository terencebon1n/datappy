import 'package:frontend/domain/nearby_stop.dart' show NearbyStop;
import 'package:frontend/infrastructure/backend/models/response/conveyance.dart'
    show ConveyanceResponse;


class NearbyStopResponse {
    final String name;
    final int distanceMeters;
    final double latitude;
    final double longitude;
    final List<ConveyanceResponse> routes;

    NearbyStopResponse({
        required this.name,
        required this.distanceMeters,
        required this.latitude,
        required this.longitude,
        required this.routes,
    });

    factory NearbyStopResponse.fromJson(Map<String, dynamic> json) {
        final routes = (json['routes'] as List?) ?? const [];

        return NearbyStopResponse(
            name: json['name'] as String,
            distanceMeters: (json['distance_m'] as num).round(),
            latitude: (json['latitude'] as num).toDouble(),
            longitude: (json['longitude'] as num).toDouble(),
            routes: routes
                .map((e) => ConveyanceResponse.fromJson(e as Map<String, dynamic>))
                .toList(),
        );
    }

    NearbyStop toDomain() => NearbyStop(
        name: name,
        distanceMeters: distanceMeters,
        latitude: latitude,
        longitude: longitude,
        routes: routes.map((route) => route.toDomain()).toList(),
    );
}
