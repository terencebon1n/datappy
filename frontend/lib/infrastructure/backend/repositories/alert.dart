import 'dart:convert' show jsonDecode;

import 'package:http/http.dart' as http;

import 'package:frontend/domain/alert.dart' show Alert;
import 'package:frontend/domain/transit_path.dart' show TransitPath;
import 'package:frontend/domain/repositories/i_alert.dart' show IAlertRepository;
import 'package:frontend/infrastructure/backend/models/response/alert.dart' show AlertResponse;


class AlertRepository implements IAlertRepository {
    final String apiBase;
    final http.Client _client;

    AlertRepository({required this.apiBase, http.Client? client})
        : _client = client ?? http.Client();

    @override
    Future<List<Alert>> resolveAlerts(TransitPath transitPath) async {
        final uri = Uri.parse('$apiBase/alerts').replace(
            queryParameters: {
                'city': transitPath.city,
                'route_id': transitPath.routeId,
                'direction_id': transitPath.direction.directionId.toString(),
                'stop_id': transitPath.direction.stopIdOrigin,
            }
        );

        final response = await _client.get(uri);
        if (response.statusCode == 200) {
            final List jsonList = jsonDecode(response.body);
            return jsonList.map(
                (json) => AlertResponse.fromJson(json).toDomain()
            ).toList();
        } else {
            throw Exception("Failed to resolve alerts: ${response.statusCode}");
        }
    }
}
