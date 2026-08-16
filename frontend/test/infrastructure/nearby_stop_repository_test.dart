import 'dart:convert';

import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';

import 'package:frontend/domain/city.dart';
import 'package:frontend/domain/coordinates.dart';
import 'package:frontend/infrastructure/backend/models/response/nearby_stop.dart';
import 'package:frontend/infrastructure/backend/repositories/nearby_stop.dart';

const _base = 'https://api.test';
const _here = Coordinates(latitude: 43.6085, longitude: 3.8794);

Map<String, dynamic> _stopJson({List? routes}) => {
      'name': 'Comédie',
      'distance_m': 124,
      'latitude': 43.6085,
      'longitude': 3.8794,
      'routes': routes ??
          [
            {
              'id': 'T1',
              'short_name': '1',
              'long_name': 'Ligne 1',
              'color': '005CA9',
              'type': 0,
              'type_name': 'Tram',
            }
          ],
    };

void main() {
  group('NearbyStopRepository', () {
    test('sends the coordinates, radius and city header', () async {
      late http.Request seen;
      final repo = NearbyStopRepository(
        apiBase: _base,
        client: MockClient((req) async {
          seen = req;
          return http.Response(jsonEncode([_stopJson()]), 200);
        }),
      );

      await repo.resolveNearbyStops(_here, City(name: 'Montpellier'),
          radiusMeters: 1200);

      expect(seen.url.path, '/nearby-stops');
      expect(seen.url.queryParameters['latitude'], '43.6085');
      expect(seen.url.queryParameters['longitude'], '3.8794');
      expect(seen.url.queryParameters['radius_m'], '1200');
      expect(seen.headers['City'], 'montpellier');
    });

    test('defaults the radius to 800 m', () async {
      late http.Request seen;
      final repo = NearbyStopRepository(
        apiBase: _base,
        client: MockClient((req) async {
          seen = req;
          return http.Response(jsonEncode([]), 200);
        }),
      );

      await repo.resolveNearbyStops(_here, City(name: 'Montpellier'));

      expect(seen.url.queryParameters['radius_m'], '800');
    });

    test('maps a 200 response into domain stops with their routes', () async {
      final repo = NearbyStopRepository(
        apiBase: _base,
        client: MockClient(
          (req) async => http.Response(jsonEncode([_stopJson()]), 200),
        ),
      );

      final stops = await repo.resolveNearbyStops(_here, City(name: 'Nimes'));

      expect(stops.single.name, 'Comédie');
      expect(stops.single.distanceMeters, 124);
      expect(stops.single.latitude, 43.6085);
      expect(stops.single.longitude, 3.8794);
      expect(stops.single.routes.single.id, 'T1');
      expect(stops.single.routes.single.typeName, 'Tram');
    });

    test('throws on a non-200 response', () async {
      final repo = NearbyStopRepository(
        apiBase: _base,
        client: MockClient((req) async => http.Response('nope', 500)),
      );

      expect(
        repo.resolveNearbyStops(_here, City(name: 'Nimes')),
        throwsException,
      );
    });

    test('defaults to a real client when none is injected', () {
      expect(NearbyStopRepository(apiBase: _base), isNotNull);
    });
  });

  group('NearbyStopResponse', () {
    test('rounds a fractional distance', () {
      final response = NearbyStopResponse.fromJson({
        ..._stopJson(),
        'distance_m': 123.6,
      });

      expect(response.distanceMeters, 124);
    });

    test('accepts integer coordinates', () {
      final response = NearbyStopResponse.fromJson({
        ..._stopJson(),
        'latitude': 43,
        'longitude': 3,
      });

      expect(response.latitude, 43.0);
      expect(response.longitude, 3.0);
    });

    test('tolerates a missing routes list', () {
      final json = _stopJson()..remove('routes');

      expect(NearbyStopResponse.fromJson(json).routes, isEmpty);
    });

    test('tolerates an empty routes list', () {
      final response = NearbyStopResponse.fromJson(_stopJson(routes: []));

      expect(response.toDomain().routes, isEmpty);
    });
  });
}
