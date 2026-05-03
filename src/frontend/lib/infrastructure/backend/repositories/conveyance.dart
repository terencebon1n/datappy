import 'dart:convert' show jsonDecode;

import 'package:http/http.dart' as http;

import 'package:frontend/domain/conveyance.dart' show Conveyance;
import 'package:frontend/domain/route_type.dart' show RouteType;
import 'package:frontend/domain/repositories/i_conveyance.dart' show IConveyanceRepository;
import 'package:frontend/infrastructure/backend/models/response/conveyance.dart' show ConveyanceResponse;


class ConveyanceRepository implements IConveyanceRepository {
    final String apiBase;
    final Map<String, String> headers;

    ConveyanceRepository({
        required this.apiBase,
        required this.headers,
    });

    @override
    Future<List<Conveyance>> resolveConveyances(RouteType routeType) async {
        final uri = Uri.parse('$apiBase/conveyance').replace(
            queryParameters: {
                'id': routeType.id.toString(),
                'name': routeType.name,
            });
        final response = await http.get(uri, headers: headers);
        if (response.statusCode == 200) {
            final List jsonList = jsonDecode(response.body);
            final List<Conveyance> conveyances = jsonList.map(
                (json) => ConveyanceResponse.fromJson(json).toDomain()
            ).toList();
            return conveyances;
        } else {
            throw Exception("Failed to resolve conveyances: ${response.statusCode}");
        }
    }
}
