import 'dart:convert' show jsonDecode;

import 'package:web_socket_channel/web_socket_channel.dart' show WebSocketChannel;

import 'package:frontend/domain/stop_update.dart' show StopUpdate;
import 'package:frontend/domain/transit_path.dart' show TransitPath;
import 'package:frontend/domain/repositories/i_stop_update.dart' show IStopUpdateRepository;
import 'package:frontend/infrastructure/backend/models/response/stop_update.dart' show StopUpdateResponse;


class StopUpdateRepository implements IStopUpdateRepository {
    final String wsBase;

    StopUpdateRepository({required this.wsBase});

    @override
    Stream<List<StopUpdate>> watchStopUpdates(TransitPath transitPath) {
        final channel = WebSocketChannel.connect(
            Uri.parse('$wsBase/stop-updates').replace(
                queryParameters: {
                    'city': transitPath.city,
                    'route_id': transitPath.routeId,
                    'direction_id': transitPath.direction.directionId.toString(),
                    'stop_id__origin': transitPath.direction.stopIdOrigin,
                    'stop_id__destination': transitPath.direction.stopIdDestination,
                }
            )
        );

        return channel.stream.map((data) {
            final List decoded = jsonDecode(data);
            return decoded.map(
                (e) => StopUpdateResponse.fromJson(e).toDomain()
            ).toList();
        });
    }

}
