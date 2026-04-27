class StopUpdate {
    final String tripId;
    final int? arrivalTime;
    final int? arrivalDelay;
    final int departureTime;
    final int? departureDelay;

    StopUpdate({
        required this.tripId,
        this.arrivalTime,
        this.arrivalDelay,
        required this.departureTime,
        this.departureDelay
    });

    factory StopUpdate.fromJson(Map<String, dynamic> json) => StopUpdate(
        tripId: json['tripId'],
        arrivalTime: json['arrivalTime'],
        arrivalDelay: json['arrivalDelay'] ?? 0,
        departureTime: json['departureTime'],
        departureDelay: json['departureDelay'] ?? 0,
    );
}
