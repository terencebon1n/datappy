import 'package:frontend/domain/stop_departure.dart' show StopDeparture;


int? parseRouteColor(String? color) {
    if (color == null || color.isEmpty) return null;
    return int.tryParse('0xFF${color.replaceFirst('#', '')}');
}

class StopDepartureResponse {
    final String tripId;
    final String routeId;
    final String routeShortName;
    final int? routeColorValue;
    final int routeTypeId;
    final int directionId;
    final String headsign;
    final int departureTime;
    final int departureDelay;
    final bool isRealtime;

    StopDepartureResponse({
        required this.tripId,
        required this.routeId,
        required this.routeShortName,
        required this.routeTypeId,
        required this.directionId,
        required this.headsign,
        required this.departureTime,
        required this.departureDelay,
        required this.isRealtime,
        this.routeColorValue,
    });

    factory StopDepartureResponse.fromJson(Map<String, dynamic> json) =>
        StopDepartureResponse(
            tripId: json['trip_id'] as String,
            routeId: json['route_id'] as String? ?? '',
            routeShortName: json['route_short_name'] as String? ?? '',
            routeColorValue: parseRouteColor(json['route_color'] as String?),
            routeTypeId: (json['route_type'] as num?)?.toInt() ?? 3,
            directionId: (json['direction_id'] as num).toInt(),
            headsign: json['headsign'] as String? ?? '',
            departureTime: (json['departure_time'] as num).toInt(),
            departureDelay: (json['departure_delay'] as num?)?.toInt() ?? 0,
            isRealtime: json['is_realtime'] as bool? ?? false,
        );

    StopDeparture toDomain() => StopDeparture(
        tripId: tripId,
        routeId: routeId,
        routeShortName: routeShortName,
        routeColorValue: routeColorValue,
        routeTypeId: routeTypeId,
        directionId: directionId,
        headsign: headsign,
        departureTime: departureTime,
        departureDelay: departureDelay,
        isRealtime: isRealtime,
    );
}
