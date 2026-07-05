class StopUpdate {
    final String tripId;
    final int? arrivalTime;
    final int arrivalDelay;
    final int departureTime;
    final int? departureDelay;
    final bool isRealtime;

    StopUpdate({
        required this.tripId,
        this.arrivalTime,
        required this.arrivalDelay,
        required this.departureTime,
        this.departureDelay,
        required this.isRealtime,
    });
}
