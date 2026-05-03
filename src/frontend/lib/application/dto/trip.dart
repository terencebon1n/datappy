import 'package:frontend/domain/direction.dart';
import 'package:frontend/domain/path.dart';

class PathDTO {
    final String routeId;
    final String stopNameOrigin;
    final String stopNameDestination;

    PathDTO({
        required this.routeId,
        required this.stopNameOrigin,
        required this.stopNameDestination,
    });

    factory PathDTO.fromJson(Map<String, dynamic> json) => PathDTO(
        routeId: json['route_id'],
        stopNameOrigin: json['stop_name__origin'],
        stopNameDestination: json['stop_name__destination'],
    );

    Path toDomain() => Path(
        routeId: routeId,
        stopNameOrigin: stopNameOrigin,
        stopNameDestination: stopNameDestination,
    );

}

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

    Direction toDomain() => Direction(
        directionId: directionId,
        stopIdOrigin: stopIdOrigin,
        stopIdDestination: stopIdDestination,
    );
}
