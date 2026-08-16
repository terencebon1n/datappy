import 'dart:async' show unawaited;
import 'dart:convert' show jsonDecode;

import 'package:web_socket_channel/web_socket_channel.dart' show WebSocketChannel;

import 'package:frontend/domain/transit_path.dart' show TransitPath;
import 'package:frontend/domain/vehicle_position.dart' show VehiclePosition;
import 'package:frontend/domain/repositories/i_vehicle_position.dart'
    show IVehiclePositionRepository;
import 'package:frontend/infrastructure/backend/models/response/vehicle_position.dart'
    show VehiclePositionResponse;


class VehiclePositionRepository implements IVehiclePositionRepository {
    final String wsBase;

    VehiclePositionRepository({required this.wsBase});

    @override
    Stream<List<VehiclePosition>> watchVehiclePositions(
        TransitPath transitPath,
    ) async* {
        final channel = WebSocketChannel.connect(
            Uri.parse('$wsBase/vehicle-positions').replace(
                queryParameters: {
                    'city': transitPath.city,
                    'route_id': transitPath.routeId,
                }
            )
        );

        try {
            await channel.ready;
            yield* channel.stream.map((data) {
                final List decoded = jsonDecode(data);
                return decoded
                    .map((e) => VehiclePositionResponse.fromJson(e).toDomain())
                    .toList();
            });
        } finally {
            unawaited(channel.sink.close().catchError((_) {}));
        }
    }
}
