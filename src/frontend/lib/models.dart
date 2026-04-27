// 1. RouteTypeDTO
class RouteTypeDTO {
  final int id;
  final String name;

  RouteTypeDTO({required this.id, required this.name});

  factory RouteTypeDTO.fromJson(Map<String, dynamic> json) => RouteTypeDTO(
        id: json['id'],
        name: json['name'],
      );
}

// 2. ConveyanceDTO
class ConveyanceDTO {
  final String id;
  final String shortName;
  final String longName;

  ConveyanceDTO({
    required this.id,
    required this.shortName,
    required this.longName,
  });

  // Getter to mimic your frontend logic for displaying names
  String get displayName => "$shortName - $longName";

  factory ConveyanceDTO.fromJson(Map<String, dynamic> json) => ConveyanceDTO(
        id: json['id'],
        shortName: json['short_name'] ?? '',
        longName: json['long_name'] ?? '',
      );
}

// 3. StopNameDTO
class StopNameDTO {
  final String name;

  StopNameDTO({required this.name});

  factory StopNameDTO.fromJson(Map<String, dynamic> json) => StopNameDTO(
        name: json['name'],
      );
}

// 4. DirectionDTO (The result of PathDTO resolution)
class DirectionDTO {
  final int directionId;
  final String stopIdOrigin;
  final String stopIdDestination;

  DirectionDTO({
    required this.directionId,
    required this.stopIdOrigin,
    required this.stopIdDestination,
  });

  factory DirectionDTO.fromJson(Map<String, dynamic> json) => DirectionDTO(
        directionId: json['direction_id'],
        stopIdOrigin: json['stop_id__origin'],
        stopIdDestination: json['stop_id__destination'],
      );
}

// 5. StopUpdate (For the WebSocket Feed)
class StopUpdate {
  final String tripId;
  final int? arrivalTime;
  final int? departureTime;
  final int arrivalDelay;

  StopUpdate({
    required this.tripId,
    this.arrivalTime,
    this.departureTime,
    required this.arrivalDelay,
  });

  factory StopUpdate.fromJson(Map<String, dynamic> json) => StopUpdate(
        tripId: json['trip_id'],
        arrivalTime: json['arrival_time'],
        departureTime: json['departure_time'],
        arrivalDelay: json['arrival_delay'] ?? 0,
      );
}
