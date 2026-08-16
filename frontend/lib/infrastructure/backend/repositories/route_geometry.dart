import 'dart:convert' show jsonDecode;

import 'package:http/http.dart' as http;

import 'package:frontend/domain/city.dart' show City;
import 'package:frontend/domain/route_geometry.dart' show RouteGeometry;
import 'package:frontend/domain/repositories/i_route_geometry.dart'
    show IRouteGeometryRepository;
import 'package:frontend/infrastructure/backend/city_header.dart' show cityHeaders;
import 'package:frontend/infrastructure/backend/models/response/route_geometry.dart'
    show RouteGeometryResponse;


class RouteGeometryRepository implements IRouteGeometryRepository {
    final String apiBase;
    final http.Client _client;

    RouteGeometryRepository({required this.apiBase, http.Client? client})
        : _client = client ?? http.Client();

    @override
    Future<RouteGeometry> resolveRouteGeometry(String routeId, City city) async {
        final uri = Uri.parse('$apiBase/route-geometry').replace(
            queryParameters: {
                'route_id': routeId,
            });

        final response = await _client.get(uri, headers: cityHeaders(city));
        if (response.statusCode == 200) {
            return RouteGeometryResponse.fromJson(jsonDecode(response.body))
                .toDomain();
        } else {
            throw Exception('Failed to load route geometry');
        }
    }
}
