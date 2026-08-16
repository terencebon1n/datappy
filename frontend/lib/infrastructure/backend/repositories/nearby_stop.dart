import 'dart:convert' show jsonDecode;

import 'package:http/http.dart' as http;

import 'package:frontend/domain/city.dart' show City;
import 'package:frontend/domain/coordinates.dart' show Coordinates;
import 'package:frontend/domain/nearby_stop.dart' show NearbyStop;
import 'package:frontend/domain/repositories/i_nearby_stop.dart'
    show INearbyStopRepository;
import 'package:frontend/infrastructure/backend/city_header.dart' show cityHeaders;
import 'package:frontend/infrastructure/backend/models/response/nearby_stop.dart'
    show NearbyStopResponse;


class NearbyStopRepository implements INearbyStopRepository {
    final String apiBase;
    final http.Client _client;

    NearbyStopRepository({required this.apiBase, http.Client? client})
        : _client = client ?? http.Client();

    @override
    Future<List<NearbyStop>> resolveNearbyStops(
        Coordinates coordinates,
        City city, {
        int radiusMeters = 800,
    }) async {
        final uri = Uri.parse('$apiBase/nearby-stops').replace(
            queryParameters: {
                'latitude': coordinates.latitude.toString(),
                'longitude': coordinates.longitude.toString(),
                'radius_m': radiusMeters.toString(),
            });

        final response = await _client.get(uri, headers: cityHeaders(city));
        if (response.statusCode == 200) {
            final List jsonList = jsonDecode(response.body);
            return jsonList
                .map((e) =>
                    NearbyStopResponse.fromJson(e as Map<String, dynamic>).toDomain())
                .toList();
        } else {
            throw Exception('Failed to load nearby stops');
        }
    }
}
