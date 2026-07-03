import 'package:frontend/domain/city.dart' show City;

Map<String, String> cityHeaders(City city) => {'City': city.name.toLowerCase()};
