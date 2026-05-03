import 'package:frontend/domain/stop_update.dart' show StopUpdate;


class StopUpdateResponse {
    final String tripId;
    final int? arrivalTime;
    final int arrivalDelay;
    final int departureTime;
    final int? departureDelay;

    StopUpdateResponse({
        required this.tripId,
        this.arrivalTime,
        required this.arrivalDelay,
        required this.departureTime,
        this.departureDelay
    });

    factory StopUpdateResponse.fromJson(Map<String, dynamic> json) => StopUpdateResponse(
        tripId: json['trip_id'],
        arrivalTime: json['arrival_time'],
        arrivalDelay: json['arrival_delay'] ?? 0,
        departureTime: json['departure_time'],
        departureDelay: json['departure_delay'] ?? 0,
    );

    StopUpdate toDomain() => StopUpdate(
        tripId: tripId,
        arrivalTime: arrivalTime,
        arrivalDelay: arrivalDelay,
        departureTime: departureTime,
        departureDelay: departureDelay,
    );
}
