import 'package:frontend/domain/city.dart' show City;


abstract class ICityRepository {
    Future<List<City>> resolveCities();
}
