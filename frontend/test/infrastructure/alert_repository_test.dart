import 'dart:convert';

import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';

import 'package:frontend/domain/alert.dart';
import 'package:frontend/infrastructure/backend/models/response/alert.dart';
import 'package:frontend/infrastructure/backend/repositories/alert.dart';

import '../helpers/fakes.dart';

const _base = 'https://api.test';

const _payload = {
  'id': 'a1',
  'cause': 'STRIKE',
  'effect': 'NO_SERVICE',
  'severity': 'SEVERE',
  'header_text': 'Grève',
  'description_text': 'Aucun service',
  'url': 'https://info.fr',
};

void main() {
  group('AlertRepository', () {
    test('parses alerts and sends the full selection as query params', () async {
      late Uri seenUri;
      final repo = AlertRepository(
        apiBase: _base,
        client: MockClient((req) async {
          seenUri = req.url;
          return http.Response(jsonEncode([_payload]), 200);
        }),
      );

      final alerts = await repo.resolveAlerts(sampleTransitPath());

      expect(seenUri.path, '/alerts');
      expect(seenUri.queryParameters, {
        'city': 'lyon',
        'route_id': 'T1',
        'direction_id': '0',
        'stop_id': 'stop_origin',
      });
      expect(alerts.single.id, 'a1');
      expect(alerts.single.severity, AlertSeverity.severe);
      expect(alerts.single.url, 'https://info.fr');
    });

    test('returns an empty list when there is no alert', () async {
      final repo = AlertRepository(
        apiBase: _base,
        client: MockClient((_) async => http.Response('[]', 200)),
      );

      expect(await repo.resolveAlerts(sampleTransitPath()), isEmpty);
    });

    test('throws on a non-200 response', () async {
      final repo = AlertRepository(
        apiBase: _base,
        client: MockClient((_) async => http.Response('nope', 500)),
      );

      expect(
        () => repo.resolveAlerts(sampleTransitPath()),
        throwsA(isA<Exception>()),
      );
    });

    test('defaults to a real client when none is injected', () {
      expect(AlertRepository(apiBase: _base), isNotNull);
    });
  });

  group('AlertResponse', () {
    test('maps every field to the domain', () {
      final alert = AlertResponse.fromJson(Map.of(_payload)).toDomain();

      expect(alert.id, 'a1');
      expect(alert.cause, 'STRIKE');
      expect(alert.effect, 'NO_SERVICE');
      expect(alert.headerText, 'Grève');
      expect(alert.descriptionText, 'Aucun service');
    });

    test('falls back on missing optional fields', () {
      final alert = AlertResponse.fromJson({'id': 'a1'}).toDomain();

      expect(alert.cause, 'UNKNOWN_CAUSE');
      expect(alert.effect, 'UNKNOWN_EFFECT');
      expect(alert.severity, AlertSeverity.unknown);
      expect(alert.headerText, '');
      expect(alert.descriptionText, '');
      expect(alert.url, isNull);
    });

    test('maps every severity code', () {
      expect(AlertSeverity.fromCode('SEVERE'), AlertSeverity.severe);
      expect(AlertSeverity.fromCode('WARNING'), AlertSeverity.warning);
      expect(AlertSeverity.fromCode('INFO'), AlertSeverity.info);
      expect(AlertSeverity.fromCode('UNKNOWN_SEVERITY'), AlertSeverity.unknown);
      expect(AlertSeverity.fromCode(null), AlertSeverity.unknown);
    });
  });
}
