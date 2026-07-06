import 'dart:convert' show jsonDecode;

import 'package:http/http.dart' as http;

import 'package:frontend/domain/city.dart' show City;
import 'package:frontend/domain/repositories/i_city.dart' show ICityRepository;
import 'package:frontend/infrastructure/backend/models/response/city.dart' show CityResponse;


class CityRepository implements ICityRepository {
    final String apiBase;

    CityRepository({required this.apiBase});

    @override
    Future<List<City>> resolveCities() async {
        final uri = Uri.parse('$apiBase/city');
        final response = await http.get(uri);
        if (response.statusCode == 200) {
            final List jsonList = jsonDecode(response.body);
            final List<City> cities = jsonList.map(
                (json) => CityResponse.fromJson(json).toDomain()
            ).toList();
            return cities;
        } else {
            throw Exception("Failed to resolve cities: ${response.statusCode}");
        }
    }
}
