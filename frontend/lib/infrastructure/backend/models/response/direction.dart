import 'package:frontend/domain/direction.dart' show Direction;


class DirectionResponse {
    final int directionId;
    final String stopIdOrigin;
    final String stopIdDestination;

    DirectionResponse({
        required this.directionId,
        required this.stopIdOrigin,
        required this.stopIdDestination,
    });

    factory DirectionResponse.fromJson(Map<String, dynamic> json) {
        return DirectionResponse(
            directionId: json['direction_id'],
            stopIdOrigin: json['stop_id__origin'],
            stopIdDestination: json['stop_id__destination'],
        );
    }

    Direction toDomain() {
        return Direction(
            directionId: directionId,
            stopIdOrigin: stopIdOrigin,
            stopIdDestination: stopIdDestination,
        );
    }
}
