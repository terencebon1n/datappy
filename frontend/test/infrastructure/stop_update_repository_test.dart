import 'dart:convert';
import 'dart:io';

import 'package:flutter_test/flutter_test.dart';

import 'package:frontend/domain/direction.dart';
import 'package:frontend/domain/transit_path.dart';
import 'package:frontend/infrastructure/backend/repositories/stop_update.dart';

TransitPath _path() => TransitPath(
      city: 'lyon',
      routeId: 'T1',
      direction: Direction(directionId: 0, stopIdOrigin: 'o', stopIdDestination: 'd'),
    );

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  test('maps a non-empty websocket payload to domain updates', () async {
    final server = await HttpServer.bind(InternetAddress.loopbackIPv4, 0);
    server.listen((req) async {
      final ws = await WebSocketTransformer.upgrade(req);
      ws.add(jsonEncode([
        {
          'trip_id': 't1',
          'departure_time': 1234,
          'arrival_delay': 5,
          'is_realtime': true,
        }
      ]));
    });

    final repo = StopUpdateRepository(wsBase: 'ws://127.0.0.1:${server.port}');
    final first = await repo.watchStopUpdates(_path()).first;

    expect(first, hasLength(1));
    expect(first.single.tripId, 't1');
    expect(first.single.departureTime, 1234);

    await server.close(force: true);
  }, timeout: const Timeout(Duration(seconds: 30)));
}
