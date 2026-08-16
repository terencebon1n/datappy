import 'package:frontend/domain/vehicle_position.dart' show VehiclePosition;


class VehiclePositionResponse {
    final String id;
    final String tripId;
    final String routeId;
    final int directionId;
    final double latitude;
    final double longitude;
    final int bearing;
    final int speed;
    final String currentStatus;
    final int timestamp;

    VehiclePositionResponse({
        required this.id,
        required this.tripId,
        required this.routeId,
        required this.directionId,
        required this.latitude,
        required this.longitude,
        required this.bearing,
        required this.speed,
        required this.currentStatus,
        required this.timestamp,
    });

    factory VehiclePositionResponse.fromJson(Map<String, dynamic> json) =>
        VehiclePositionResponse(
            id: json['id'] as String,
            tripId: json['trip_id'] as String,
            routeId: json['route_id'] as String,
            directionId: (json['direction_id'] as num).toInt(),
            latitude: (json['latitude'] as num).toDouble(),
            longitude: (json['longitude'] as num).toDouble(),
            bearing: (json['bearing'] as num).toInt(),
            speed: (json['speed'] as num).toInt(),
            currentStatus: json['current_status'] as String? ?? '',
            timestamp: (json['timestamp'] as num).toInt(),
        );

    VehiclePosition toDomain() => VehiclePosition(
        id: id,
        tripId: tripId,
        routeId: routeId,
        directionId: directionId,
        latitude: latitude,
        longitude: longitude,
        bearing: bearing,
        speed: speed,
        currentStatus: currentStatus,
        timestamp: timestamp,
    );
}
