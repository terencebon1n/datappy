import 'dart:convert';
import 'dart:io';

import 'package:flutter_test/flutter_test.dart';

import 'package:frontend/domain/direction.dart';
import 'package:frontend/domain/transit_path.dart';
import 'package:frontend/infrastructure/backend/models/response/vehicle_position.dart';
import 'package:frontend/infrastructure/backend/repositories/vehicle_position.dart';

TransitPath _path() => TransitPath(
      city: 'montpellier',
      routeId: 'T1',
      direction:
          Direction(directionId: 0, stopIdOrigin: 'o', stopIdDestination: 'd'),
    );

Map<String, dynamic> _payload({String id = 'v1'}) => {
      'id': id,
      'trip_id': 't1',
      'route_id': 'T1',
      'direction_id': 0,
      'latitude': 43.6085,
      'longitude': 3.8794,
      'bearing': 90,
      'speed': 12,
      'current_status': 'IN_TRANSIT_TO',
      'timestamp': 1700000000,
    };

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  test('maps a websocket payload to domain vehicle positions', () async {
    final server = await HttpServer.bind(InternetAddress.loopbackIPv4, 0);
    late Uri requested;
    server.listen((req) async {
      requested = req.uri;
      final ws = await WebSocketTransformer.upgrade(req);
      ws.add(jsonEncode([_payload()]));
    });

    final repo =
        VehiclePositionRepository(wsBase: 'ws://127.0.0.1:${server.port}');
    final first = await repo.watchVehiclePositions(_path()).first;

    expect(requested.path, '/vehicle-positions');
    expect(requested.queryParameters['city'], 'montpellier');
    expect(requested.queryParameters['route_id'], 'T1');
    expect(first, hasLength(1));
    expect(first.single.id, 'v1');
    expect(first.single.latitude, 43.6085);
    expect(first.single.bearing, 90);

    await server.close(force: true);
  }, timeout: const Timeout(Duration(seconds: 30)));

  test('maps an empty payload to no vehicles', () async {
    final server = await HttpServer.bind(InternetAddress.loopbackIPv4, 0);
    server.listen((req) async {
      final ws = await WebSocketTransformer.upgrade(req);
      ws.add(jsonEncode([]));
    });

    final repo =
        VehiclePositionRepository(wsBase: 'ws://127.0.0.1:${server.port}');

    expect(await repo.watchVehiclePositions(_path()).first, isEmpty);

    await server.close(force: true);
  }, timeout: const Timeout(Duration(seconds: 30)));

  test('response accepts integer coordinates and a missing status', () {
    final response = VehiclePositionResponse.fromJson({
      ..._payload(),
      'latitude': 43,
      'longitude': 3,
      'current_status': null,
    });

    expect(response.latitude, 43.0);
    expect(response.longitude, 3.0);
    expect(response.currentStatus, '');
    expect(response.toDomain().id, 'v1');
  });
}
