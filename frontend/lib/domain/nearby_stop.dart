import 'package:frontend/domain/conveyance.dart' show Conveyance;


class NearbyStop {
    final String name;
    final int distanceMeters;
    final double latitude;
    final double longitude;
    final List<Conveyance> routes;

    const NearbyStop({
        required this.name,
        required this.distanceMeters,
        required this.latitude,
        required this.longitude,
        required this.routes,
    });
}
