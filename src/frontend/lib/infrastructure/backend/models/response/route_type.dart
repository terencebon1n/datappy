import 'package:frontend/domain/route_type.dart' show RouteType;


class RouteTypeResponse {
    final int id;
    final String name;

    RouteTypeResponse({
        required this.id,
        required this.name,
    });

    factory RouteTypeResponse.fromJson(Map<String, dynamic> json) => RouteTypeResponse(
        id: json['id'],
        name: json['name'],
    ); 

    RouteType toDomain() => RouteType(
        id: id,
        name: name,
    );
}
