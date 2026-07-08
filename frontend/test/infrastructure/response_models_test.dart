import 'package:flutter_test/flutter_test.dart';

import 'package:frontend/infrastructure/backend/models/response/city.dart';
import 'package:frontend/infrastructure/backend/models/response/conveyance.dart';
import 'package:frontend/infrastructure/backend/models/response/direction.dart';
import 'package:frontend/infrastructure/backend/models/response/stop_update.dart';

void main() {
  group('CityResponse', () {
    test('capitalizes a non-empty name', () {
      expect(CityResponse.fromJson('lyon').toDomain().name, 'Lyon');
    });

    test('leaves an empty name untouched', () {
      expect(CityResponse.fromJson('').toDomain().name, '');
    });
  });

  group('ConveyanceResponse', () {
    Map<String, dynamic> base(String? color) => {
          'id': 'T1',
          'short_name': 'T1',
          'long_name': 'Tram 1',
          'color': color,
          'type': 0,
          'type_name': 'Tramway',
        };

    test('parses a hex color into an ARGB value', () {
      final c = ConveyanceResponse.fromJson(base('#0080C0')).toDomain();
      expect(c.colorValue, 0xFF0080C0);
      expect(c.id, 'T1');
    });

    test('falls back to white when color is null', () {
      expect(ConveyanceResponse.fromJson(base(null)).colorValue, 0xFFFFFFFF);
    });

    test('falls back to white when color is unparseable', () {
      expect(ConveyanceResponse.fromJson(base('#ZZZZZZ')).colorValue, 0xFFFFFFFF);
    });
  });

  group('DirectionResponse', () {
    test('maps every field to the domain', () {
      final d = DirectionResponse.fromJson({
        'direction_id': 1,
        'stop_id__origin': 'o',
        'stop_id__destination': 'd',
      }).toDomain();
      expect(d.directionId, 1);
      expect(d.stopIdOrigin, 'o');
      expect(d.stopIdDestination, 'd');
    });
  });

  group('StopUpdateResponse', () {
    test('reads all provided fields', () {
      final s = StopUpdateResponse.fromJson({
        'trip_id': 't1',
        'arrival_time': 100,
        'arrival_delay': 30,
        'departure_time': 120,
        'departure_delay': 45,
        'is_realtime': false,
      }).toDomain();
      expect(s.tripId, 't1');
      expect(s.arrivalTime, 100);
      expect(s.arrivalDelay, 30);
      expect(s.departureDelay, 45);
      expect(s.isRealtime, isFalse);
    });

    test('applies defaults for missing fields', () {
      final s = StopUpdateResponse.fromJson({
        'trip_id': 't1',
        'departure_time': 120,
      }).toDomain();
      expect(s.arrivalDelay, 0);
      expect(s.departureDelay, 0);
      expect(s.isRealtime, isTrue);
      expect(s.arrivalTime, isNull);
    });
  });
}
