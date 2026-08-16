import 'dart:convert' show jsonDecode;

import 'package:http/http.dart' as http;

import 'package:frontend/domain/city.dart' show City;
import 'package:frontend/domain/stop_departure.dart' show StopDeparture;
import 'package:frontend/domain/repositories/i_stop_departure.dart'
    show IStopDepartureRepository;
import 'package:frontend/infrastructure/backend/city_header.dart' show cityHeaders;
import 'package:frontend/infrastructure/backend/models/response/stop_departure.dart'
    show StopDepartureResponse;


class StopDepartureRepository implements IStopDepartureRepository {
    final String apiBase;
    final http.Client _client;

    StopDepartureRepository({required this.apiBase, http.Client? client})
        : _client = client ?? http.Client();

    @override
    Future<List<StopDeparture>> resolveStopDepartures({
        required String stopId,
        required City city,
    }) async {
        final uri = Uri.parse('$apiBase/stop-departures').replace(
            queryParameters: {
                'city': city.name.toLowerCase(),
                'stop_id': stopId,
            });

        final response = await _client.get(uri, headers: cityHeaders(city));
        if (response.statusCode == 200) {
            final List jsonList = jsonDecode(response.body);
            return jsonList
                .map((e) =>
                    StopDepartureResponse.fromJson(e as Map<String, dynamic>).toDomain())
                .toList();
        } else {
            throw Exception('Failed to load stop departures');
        }
    }
}
