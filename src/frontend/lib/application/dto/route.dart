class RouteTypeDTO {
    final String id;
    final String name;

    RouteTypeDTO({
        required this.id,
        required this.name,
    });

    factory RouteTypeDTO.fromJson(Map<String, dynamic> json) => RouteTypeDTO(
        id: json['id'],
        name: json['name'],
    );

    Map<String, dynamic> toQueryParameters() => {
        'id': id,
        'name': name,
    };
}

class RouteIdDTO {
    final String routeId;

    RouteIdDTO({
        required this.routeId,
    });

    factory RouteIdDTO.fromJson(Map<String, dynamic> json) => RouteIdDTO(
        routeId: json['route_id'],
    );

    Map<String, dynamic> toQueryParameters() => {
        'route_id': routeId.toString(),
    };
}

class ConveyanceDTO {
    final String id;
    final String shortName;
    final String longName;

    ConveyanceDTO({
        required this.id,
        required this.shortName,
        required this.longName,
    });

    String get displayName => "$shortName - $longName";

    factory ConveyanceDTO.fromJson(Map<String, dynamic> json) => ConveyanceDTO(
        id: json['id'],
        shortName: json['short_name'],
        longName: json['long_name'],
    );
}
