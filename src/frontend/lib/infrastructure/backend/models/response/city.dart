import 'package:frontend/domain/city.dart' show City;


class CityResponse {
    final String name;

    CityResponse({
        required this.name,
    });

    factory CityResponse.fromJson(String name) {
        final capitalizedName = name.isNotEmpty 
            ? '${name[0].toUpperCase()}${name.substring(1)}' 
            : name;

        return CityResponse(
            name: capitalizedName,
        );
    }

    City toDomain() {
        return City(
            name: name,
        );
    }
}
