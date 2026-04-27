import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:frontend/domain/direction.dart';
import 'package:frontend/domain/repositories/i_direction.dart';
import 'package:frontend/application/dto/trip.dart';

class DirectionRepository implements IDirectionRepository {
  final String apiBase;
  final Map<String, String> headers;

  DirectionRepository({
    required this.apiBase, 
    required this.headers,
  });

  @override
  Future<Direction> resolveDirection({
    required String routeId,
    required String originName,
    required String destinationName,
  }) async {
    final uri = Uri.parse('$apiBase/direction').replace(queryParameters: {
      'route_id': routeId,
      'stop_name__origin': originName,
      'stop_name__destination': destinationName,
    });

    final response = await http.get(uri, headers: headers);

    if (response.statusCode == 200) {

      final Map<String, dynamic> jsonData = jsonDecode(response.body);
      final dto = DirectionDTO.fromJson(jsonData);
      return dto.toDomain();

    } else {
      throw Exception("Failed to resolve transit direction: ${response.statusCode}");
    }
  }
}
