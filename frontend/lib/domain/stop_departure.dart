class StopDeparture {
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

    const StopDeparture({
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
}
