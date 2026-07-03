import 'dart:convert' show jsonDecode;

import 'package:http/http.dart' as http;

import 'package:frontend/domain/city.dart' show City;
import 'package:frontend/domain/repositories/i_stop_name.dart' show IStopNameRepository;
import 'package:frontend/infrastructure/backend/city_header.dart' show cityHeaders;


class StopNameRepository implements IStopNameRepository {
    final String apiBase;

    StopNameRepository({required this.apiBase});

    @override
    Future<List<String>> resolveStopNames(String routeId, City city) async {
        final uri = Uri.parse('$apiBase/stop').replace(
            queryParameters: {
                'route_id': routeId,
            });

        final response = await http.get(uri, headers: cityHeaders(city));
        if (response.statusCode == 200) {
            final List jsonList = jsonDecode(response.body);
            return jsonList.map((e) => e['name'].toString()).toList();
        } else {
            throw Exception('Failed to load stop names');
        }
    }
}
