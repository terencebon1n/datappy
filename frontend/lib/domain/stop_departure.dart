class StopDeparture {
    final String tripId;
    final int directionId;
    final String headsign;
    final int departureTime;
    final int departureDelay;
    final bool isRealtime;

    const StopDeparture({
        required this.tripId,
        required this.directionId,
        required this.headsign,
        required this.departureTime,
        required this.departureDelay,
        required this.isRealtime,
    });
}
