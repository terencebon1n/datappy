import 'dart:convert';

import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';

import 'package:frontend/domain/city.dart';
import 'package:frontend/infrastructure/backend/models/response/route_geometry.dart';
import 'package:frontend/infrastructure/backend/repositories/route_geometry.dart';

const _base = 'https://api.test';

Map<String, dynamic> _payload() => {
      'shapes': [
        {
          'direction_id': 0,
          'points': [
            {'latitude': 43.60, 'longitude': 3.87},
            {'latitude': 43.61, 'longitude': 3.88},
          ],
        }
      ],
      'stops': [
        {
          'id': 's1',
          'name': 'Comédie',
          'latitude': 43.6085,
          'longitude': 3.8794,
          'code': '1234',
          'platform_code': 'B',
          'wheelchair_boarding': 1,
        }
      ],
      'direction_headsigns': [
        {'direction_id': 0, 'headsign': 'Mosson'},
        {'direction_id': 1, 'headsign': 'Odysseum'},
      ],
    };

void main() {
  group('RouteGeometryRepository', () {
    test('sends the route id and city header', () async {
      late http.Request seen;
      final repo = RouteGeometryRepository(
        apiBase: _base,
        client: MockClient((req) async {
          seen = req;
          return http.Response(jsonEncode(_payload()), 200);
        }),
      );

      await repo.resolveRouteGeometry('T1', City(name: 'Montpellier'));

      expect(seen.url.path, '/route-geometry');
      expect(seen.url.queryParameters['route_id'], 'T1');
      expect(seen.headers['City'], 'montpellier');
    });

    test('maps a 200 response into domain geometry', () async {
      final repo = RouteGeometryRepository(
        apiBase: _base,
        client: MockClient(
          (req) async => http.Response(jsonEncode(_payload()), 200),
        ),
      );

      final geometry =
          await repo.resolveRouteGeometry('T1', City(name: 'Nimes'));

      expect(geometry.shapes.single.directionId, 0);
      expect(geometry.shapes.single.points, hasLength(2));
      expect(geometry.shapes.single.points.first.latitude, 43.60);
      expect(geometry.stops.single.name, 'Comédie');
      expect(geometry.stops.single.code, '1234');
      expect(geometry.stops.single.platformCode, 'B');
      expect(geometry.stops.single.isWheelchairAccessible, isTrue);
      expect(geometry.headsignFor(0), 'Mosson');
      expect(geometry.headsignFor(1), 'Odysseum');
      expect(geometry.headsignFor(9), isNull);
    });

    test('treats a blank headsign as empty', () async {
      final repo = RouteGeometryRepository(
        apiBase: _base,
        client: MockClient(
          (req) async => http.Response(
            jsonEncode({
              'shapes': [],
              'stops': [],
              'direction_headsigns': [
                {'direction_id': 0, 'headsign': null},
              ],
            }),
            200,
          ),
        ),
      );

      final geometry =
          await repo.resolveRouteGeometry('T1', City(name: 'Nimes'));

      expect(geometry.headsignFor(0), '');
    });

    test('a stop without accessibility data is neither flag', () async {
      final repo = RouteGeometryRepository(
        apiBase: _base,
        client: MockClient(
          (req) async => http.Response(
            jsonEncode({
              'shapes': [],
              'stops': [
                {
                  'id': 's1',
                  'name': 'A',
                  'latitude': 43.6,
                  'longitude': 3.87,
                }
              ],
            }),
            200,
          ),
        ),
      );

      final stop =
          (await repo.resolveRouteGeometry('T1', City(name: 'Nimes'))).stops.single;

      expect(stop.isWheelchairAccessible, isFalse);
      expect(stop.isWheelchairInaccessible, isFalse);
      expect(stop.code, isNull);
    });

    test('throws on a non-200 response', () {
      final repo = RouteGeometryRepository(
        apiBase: _base,
        client: MockClient((req) async => http.Response('nope', 500)),
      );

      expect(
        repo.resolveRouteGeometry('T1', City(name: 'Nimes')),
        throwsException,
      );
    });

    test('defaults to a real client when none is injected', () {
      expect(RouteGeometryRepository(apiBase: _base), isNotNull);
    });
  });

  group('RouteGeometryResponse', () {
    test('tolerates missing shapes and stops', () {
      final response = RouteGeometryResponse.fromJson({});

      expect(response.shapes, isEmpty);
      expect(response.stops, isEmpty);
      expect(response.directionHeadsigns, isEmpty);
      expect(response.toDomain().isEmpty, isTrue);
    });

    test('tolerates a shape without points', () {
      final response = RouteGeometryResponse.fromJson({
        'shapes': [
          {'direction_id': 1}
        ],
        'stops': [],
      });

      expect(response.shapes.single.directionId, 1);
      expect(response.shapes.single.points, isEmpty);
    });

    test('accepts integer coordinates', () {
      final response = RouteGeometryResponse.fromJson({
        'shapes': [
          {
            'direction_id': 0,
            'points': [
              {'latitude': 43, 'longitude': 3}
            ],
          }
        ],
        'stops': [
          {'id': 's1', 'name': 'A', 'latitude': 43, 'longitude': 3}
        ],
      });

      expect(response.shapes.single.points.single.latitude, 43.0);
      expect(response.stops.single.longitude, 3.0);
    });
  });
}
