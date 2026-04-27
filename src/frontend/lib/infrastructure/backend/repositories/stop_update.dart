import 'dart:convert';
import 'package:frontend/domain/stop_update.dart';
import 'package:frontend/domain/repositories/i_stop_update.dart';
import 'package:web_socket_channel/web_socket_channel.dart';


class StopUpdateRepository implements IStopUpdateRepository {
    final String wsBase;

    StopUpdateRepository({required this.wsBase});

    @override
    Stream<List<StopUpdate>> watchStopUpdates(
        String city,
        String routeId,
        int directionId,
        String stopIdOrigin,
        String stopIdDestination,
    ) {
        final channel = WebSocketChannel.connect(
            Uri.parse('$wsBase/stop-updates').replace(queryParameters: {
                "city": city,
                "route_id": routeId,
                "direction_id": directionId.toString(),
                "stop_id__origin": stopIdOrigin,
                "stop_id__destination": stopIdDestination,
            })
        );

        return channel.stream.map((data) {
            final List decoded = jsonDecode(data);
            return decoded.map((e) => StopUpdate.fromJson(e)).toList();
        });
    }

}
