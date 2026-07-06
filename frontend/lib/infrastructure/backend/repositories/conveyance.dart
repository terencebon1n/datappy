import 'dart:convert' show jsonDecode;

import 'package:http/http.dart' as http;

import 'package:frontend/domain/city.dart' show City;
import 'package:frontend/domain/conveyance.dart' show Conveyance;
import 'package:frontend/domain/repositories/i_conveyance.dart' show IConveyanceRepository;
import 'package:frontend/infrastructure/backend/city_header.dart' show cityHeaders;
import 'package:frontend/infrastructure/backend/models/response/conveyance.dart' show ConveyanceResponse;


class ConveyanceRepository implements IConveyanceRepository {
    final String apiBase;

    ConveyanceRepository({required this.apiBase});

    @override
    Future<List<Conveyance>> resolveConveyances(City city) async {
        final uri = Uri.parse('$apiBase/conveyance');
        final response = await http.get(uri, headers: cityHeaders(city));
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
