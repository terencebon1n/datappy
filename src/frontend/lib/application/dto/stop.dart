class StopNameDTO {
    final String stopName;

    StopNameDTO({
        required this.stopName,
    });

    factory StopNameDTO.fromJson(Map<String, dynamic> json) => StopNameDTO(
        stopName: json['name'],
    );
}

class TransitPathDTO {
    final String city;
    final String routeId;
    final int directionId;
    final String stopIdOrigin;
    final String stopIdDestination;

    TransitPathDTO({
        required this.city,
        required this.routeId,
        required this.directionId,
        required this.stopIdOrigin,
        required this.stopIdDestination,
    });

    factory TransitPathDTO.fromJson(Map<String, dynamic> json) => TransitPathDTO(
        city: json['city'],
        routeId: json['route_id'],
        directionId: json['direction_id'],
        stopIdOrigin: json['stop_id__origin'],
        stopIdDestination: json['stop_id__destination'],
    );


    Map<String, dynamic> toJson() => {
        'city': city,
        'route_id': routeId,
        'direction_id': directionId,
        'stop_id__origin': stopIdOrigin,
        'stop_id__destination': stopIdDestination,
    };
}
