import 'dart:convert' show jsonDecode;

import 'package:http/http.dart' as http;

import 'package:frontend/domain/route_type.dart' show RouteType;
import 'package:frontend/domain/repositories/i_route_type.dart' show IRouteTypeRepository;
import 'package:frontend/infrastructure/backend/models/response/route_type.dart' show RouteTypeResponse;


class RouteTypeRepository implements IRouteTypeRepository {
    final String apiBase;
    final Map<String, String> headers;

    RouteTypeRepository({
        required this.apiBase,
        required this.headers,
    });

    @override
    Future<List<RouteType>> resolveRouteTypes() async {
        final uri = Uri.parse('$apiBase/route-type');
        final response = await http.get(uri, headers: headers);
        if (response.statusCode == 200) {
            final List jsonList = jsonDecode(response.body);
            final List<RouteType> routeTypes = jsonList.map(
                (json) => RouteTypeResponse.fromJson(json).toDomain()
            ).toList();
            return routeTypes;
        } else {
            throw Exception("Failed to resolve route types: ${response.statusCode}");
        }
    }
}
