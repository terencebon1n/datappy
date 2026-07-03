import 'package:frontend/domain/city.dart' show City;


abstract class IStopNameRepository {
    Future<List<String>> resolveStopNames(String routeId, City city);
}
