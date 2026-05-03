import 'dart:convert' show jsonDecode;

import 'package:http/http.dart' as http;

import 'package:frontend/domain/repositories/i_stop_name.dart' show IStopNameRepository;


class StopNameRepository implements IStopNameRepository {
    final String apiBase;
    final Map<String, String> headers;

    StopNameRepository({
        required this.apiBase,
        required this.headers,
    });

    @override
    Future<List<String>> resolveStopNames(String routeId) async {
        final uri = Uri.parse('$apiBase/stop').replace(
            queryParameters: {
                'route_id': routeId,
            });

        final response = await http.get(uri, headers: headers);
        if (response.statusCode == 200) {
            final List jsonList = jsonDecode(response.body);
            return jsonList.map((e) => e['name'].toString()).toList();
        } else {
            throw Exception('Failed to load stop names');
        }
    }
}
