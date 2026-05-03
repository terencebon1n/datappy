import 'dart:convert' show jsonDecode;

import 'package:http/http.dart' as http;

import 'package:frontend/application/dto/trip.dart' show DirectionDTO;
import 'package:frontend/domain/direction.dart' show Direction;
import 'package:frontend/domain/path.dart' show Path;
import 'package:frontend/domain/repositories/i_direction.dart' show IDirectionRepository;



class DirectionRepository implements IDirectionRepository {
  final String apiBase;
  final Map<String, String> headers;

  DirectionRepository({
    required this.apiBase, 
    required this.headers,
  });

  @override
  Future<Direction> resolveDirection(Path path) async {
    final uri = Uri.parse('$apiBase/direction').replace(
        queryParameters: {
            'route_id': path.routeId,
            'stop_name__origin': path.stopNameOrigin,
            'stop_name__destination': path.stopNameDestination,
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
