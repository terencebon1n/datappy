import 'package:frontend/domain/city.dart' show City;
import 'package:frontend/domain/coordinates.dart' show Coordinates;
import 'package:frontend/domain/nearby_stop.dart' show NearbyStop;


abstract class INearbyStopRepository {
    Future<List<NearbyStop>> resolveNearbyStops(
        Coordinates coordinates,
        City city, {
        int radiusMeters,
    });
}
