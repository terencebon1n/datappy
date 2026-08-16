import 'package:frontend/domain/stop_departure.dart' show StopDeparture;


class StopDepartureResponse {
    final String tripId;
    final int directionId;
    final String headsign;
    final int departureTime;
    final int departureDelay;
    final bool isRealtime;

    StopDepartureResponse({
        required this.tripId,
        required this.directionId,
        required this.headsign,
        required this.departureTime,
        required this.departureDelay,
        required this.isRealtime,
    });

    factory StopDepartureResponse.fromJson(Map<String, dynamic> json) =>
        StopDepartureResponse(
            tripId: json['trip_id'] as String,
            directionId: (json['direction_id'] as num).toInt(),
            headsign: json['headsign'] as String? ?? '',
            departureTime: (json['departure_time'] as num).toInt(),
            departureDelay: (json['departure_delay'] as num?)?.toInt() ?? 0,
            isRealtime: json['is_realtime'] as bool? ?? false,
        );

    StopDeparture toDomain() => StopDeparture(
        tripId: tripId,
        directionId: directionId,
        headsign: headsign,
        departureTime: departureTime,
        departureDelay: departureDelay,
        isRealtime: isRealtime,
    );
}
