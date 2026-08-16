import 'dart:convert';

import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';

import 'package:frontend/domain/city.dart';
import 'package:frontend/infrastructure/backend/models/response/stop_departure.dart';
import 'package:frontend/infrastructure/backend/repositories/stop_departure.dart';

const _base = 'https://api.test';

Map<String, dynamic> _payload() => {
      'trip_id': 't1',
      'route_id': 'T1',
      'route_short_name': '1',
      'route_color': '0080C0',
      'route_type': 0,
      'direction_id': 0,
      'headsign': 'Mosson',
      'departure_time': 1700000000,
      'departure_delay': 30,
      'is_realtime': true,
    };

void main() {
  test('sends route, stop and city', () async {
    late http.Request seen;
    final repo = StopDepartureRepository(
      apiBase: _base,
      client: MockClient((req) async {
        seen = req;
        return http.Response(jsonEncode([_payload()]), 200);
      }),
    );

    await repo.resolveStopDepartures(
      stopId: 's1',
      city: City(name: 'Montpellier'),
    );

    expect(seen.url.path, '/stop-departures');
    expect(seen.url.queryParameters.containsKey('route_id'), isFalse);
    expect(seen.url.queryParameters['stop_id'], 's1');
    expect(seen.url.queryParameters['city'], 'montpellier');
    expect(seen.headers['City'], 'montpellier');
  });

  test('maps a 200 response into domain departures', () async {
    final repo = StopDepartureRepository(
      apiBase: _base,
      client: MockClient(
        (req) async => http.Response(jsonEncode([_payload()]), 200),
      ),
    );

    final departures = await repo.resolveStopDepartures(
      stopId: 's1',
      city: City(name: 'Nimes'),
    );

    expect(departures.single.tripId, 't1');
    expect(departures.single.routeShortName, '1');
    expect(departures.single.routeColorValue, 0xFF0080C0);
    expect(departures.single.routeTypeId, 0);
    expect(departures.single.headsign, 'Mosson');
    expect(departures.single.departureDelay, 30);
    expect(departures.single.isRealtime, isTrue);
  });

  test('throws on a non-200 response', () {
    final repo = StopDepartureRepository(
      apiBase: _base,
      client: MockClient((req) async => http.Response('nope', 500)),
    );

    expect(
      repo.resolveStopDepartures(
        stopId: 's1',
        city: City(name: 'Nimes'),
      ),
      throwsException,
    );
  });

  test('defaults to a real client when none is injected', () {
    expect(StopDepartureRepository(apiBase: _base), isNotNull);
  });

  test('tolerates missing optional fields', () {
    final response = StopDepartureResponse.fromJson({
      'trip_id': 't1',
      'direction_id': 0,
      'departure_time': 1700000000,
    });

    expect(response.headsign, '');
    expect(response.departureDelay, 0);
    expect(response.isRealtime, isFalse);
    expect(response.routeShortName, '');
    expect(response.routeColorValue, isNull);
    expect(response.routeTypeId, 3);
    expect(response.toDomain().tripId, 't1');
  });

  test('parses route colours and tolerates junk', () {
    expect(parseRouteColor('0080C0'), 0xFF0080C0);
    expect(parseRouteColor('#0080C0'), 0xFF0080C0);
    expect(parseRouteColor(null), isNull);
    expect(parseRouteColor(''), isNull);
    expect(parseRouteColor('not-a-colour'), isNull);
  });
}
