import 'dart:convert';

import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';

import 'package:frontend/domain/city.dart';
import 'package:frontend/domain/path.dart';
import 'package:frontend/infrastructure/backend/repositories/city.dart';
import 'package:frontend/infrastructure/backend/repositories/conveyance.dart';
import 'package:frontend/infrastructure/backend/repositories/direction.dart';
import 'package:frontend/infrastructure/backend/repositories/stop_name.dart';

const _base = 'https://api.test';

MockClient okClient(String body, void Function(http.Request)? inspect) =>
    MockClient((req) async {
      inspect?.call(req);
      return http.Response(body, 200);
    });

MockClient errorClient() => MockClient((req) async => http.Response('nope', 500));

void main() {
  group('CityRepository', () {
    test('parses and capitalizes cities from a 200 response', () async {
      late Uri seenUri;
      final repo = CityRepository(
        apiBase: _base,
        client: okClient(jsonEncode(['lyon', 'paris']), (r) => seenUri = r.url),
      );

      final cities = await repo.resolveCities();

      expect(seenUri, Uri.parse('$_base/city'));
      expect(cities.map((c) => c.name), ['Lyon', 'Paris']);
    });

    test('throws on a non-200 response', () async {
      final repo = CityRepository(apiBase: _base, client: errorClient());
      expect(repo.resolveCities(), throwsException);
    });

    test('defaults to a real client when none is injected', () {
      expect(CityRepository(apiBase: _base), isNotNull);
    });
  });

  group('ConveyanceRepository', () {
    test('parses conveyances and sends the City header', () async {
      late http.Request seen;
      final repo = ConveyanceRepository(
        apiBase: _base,
        client: okClient(
          jsonEncode([
            {
              'id': 'T1',
              'short_name': 'T1',
              'long_name': 'Tram 1',
              'color': '#0080C0',
              'type': 0,
              'type_name': 'Tramway',
            }
          ]),
          (r) => seen = r,
        ),
      );

      final conveyances = await repo.resolveConveyances(City(name: 'Lyon'));

      expect(seen.url, Uri.parse('$_base/conveyance'));
      expect(seen.headers['City'], 'lyon');
      expect(conveyances.single.id, 'T1');
      expect(conveyances.single.colorValue, 0xFF0080C0);
    });

    test('throws on a non-200 response', () {
      final repo = ConveyanceRepository(apiBase: _base, client: errorClient());
      expect(repo.resolveConveyances(City(name: 'Lyon')), throwsException);
    });
  });

  group('StopNameRepository', () {
    test('parses stop names and passes route_id', () async {
      late Uri seenUri;
      final repo = StopNameRepository(
        apiBase: _base,
        client: okClient(
          jsonEncode([
            {'name': 'Perrache'},
            {'name': 'Debourg'},
          ]),
          (r) => seenUri = r.url,
        ),
      );

      final stops = await repo.resolveStopNames('T1', City(name: 'Lyon'));

      expect(seenUri.path, '/stop');
      expect(seenUri.queryParameters['route_id'], 'T1');
      expect(stops, ['Perrache', 'Debourg']);
    });

    test('throws on a non-200 response', () {
      final repo = StopNameRepository(apiBase: _base, client: errorClient());
      expect(repo.resolveStopNames('T1', City(name: 'Lyon')), throwsException);
    });
  });

  group('DirectionRepository', () {
    test('parses a direction and sends all query params', () async {
      late Uri seenUri;
      final repo = DirectionRepository(
        apiBase: _base,
        client: okClient(
          jsonEncode({
            'direction_id': 1,
            'stop_id__origin': 'o1',
            'stop_id__destination': 'd1',
          }),
          (r) => seenUri = r.url,
        ),
      );

      final direction = await repo.resolveDirection(
        Path(routeId: 'T1', stopNameOrigin: 'Perrache', stopNameDestination: 'Debourg'),
        City(name: 'Lyon'),
      );

      expect(seenUri.path, '/direction');
      expect(seenUri.queryParameters['route_id'], 'T1');
      expect(seenUri.queryParameters['stop_name__origin'], 'Perrache');
      expect(seenUri.queryParameters['stop_name__destination'], 'Debourg');
      expect(direction.directionId, 1);
      expect(direction.stopIdOrigin, 'o1');
    });

    test('throws on a non-200 response', () {
      final repo = DirectionRepository(apiBase: _base, client: errorClient());
      expect(
        repo.resolveDirection(
          Path(routeId: 'T1', stopNameOrigin: 'a', stopNameDestination: 'b'),
          City(name: 'Lyon'),
        ),
        throwsException,
      );
    });
  });
}
