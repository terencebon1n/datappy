import 'package:frontend/domain/city.dart' show City;
import 'package:frontend/domain/stop_departure.dart' show StopDeparture;


abstract class IStopDepartureRepository {
    Future<List<StopDeparture>> resolveStopDepartures({
        required String stopId,
        required City city,
    });
}
