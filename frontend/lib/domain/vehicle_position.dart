class VehiclePosition {
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

    const VehiclePosition({
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
}
