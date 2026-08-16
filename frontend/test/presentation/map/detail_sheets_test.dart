import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:flutter_test/flutter_test.dart';

import 'package:frontend/application/stop_departures/cubit.dart';
import 'package:frontend/domain/route_geometry.dart';
import 'package:frontend/presentation/map/stop_details_sheet.dart';
import 'package:frontend/presentation/map/vehicle_details_sheet.dart';
import 'package:frontend/presentation/theme/colors.dart';

import '../../helpers/fakes.dart';

final _now = DateTime.fromMillisecondsSinceEpoch(1700000000 * 1000);
int get _nowEpoch => _now.millisecondsSinceEpoch ~/ 1000;

RouteStop _stop({
  String name = 'Comédie',
  String? code,
  String? platformCode,
  int? wheelchairBoarding,
}) =>
    RouteStop(
      id: 's1',
      name: name,
      latitude: 43.6085,
      longitude: 3.8794,
      code: code,
      platformCode: platformCode,
      wheelchairBoarding: wheelchairBoarding,
    );

Future<StopDeparturesCubit> _pumpStopSheet(
  WidgetTester tester, {
  required RouteStop stop,
  FakeStopDepartureRepo? repo,
  bool load = true,
}) async {
  TransitColors.apply(false);
  final cubit = StopDeparturesCubit(repo: repo ?? FakeStopDepartureRepo());
  addTearDown(cubit.close);

  if (load) {
    await tester.runAsync(
      () => cubit.load(routeId: 'T1', stopId: 's1', city: sampleCity()),
    );
  }

  await tester.pumpWidget(
    MaterialApp(
      home: BlocProvider.value(
        value: cubit,
        child: Scaffold(
          body: StopDetailsSheet(
            stop: stop,
            routeColor: const Color(0xFF0080C0),
            now: _now,
          ),
        ),
      ),
    ),
  );
  await tester.pump();
  return cubit;
}

Future<void> _pumpVehicleSheet(
  WidgetTester tester, {
  int bearing = 90,
  int speed = 12,
  int? timestamp,
  String status = 'IN_TRANSIT_TO',
  String? headsign,
}) async {
  TransitColors.apply(false);
  await tester.pumpWidget(
    MaterialApp(
      home: Scaffold(
        body: VehicleDetailsSheet(
          vehicle: sampleVehiclePosition(
            bearing: bearing,
            speed: speed,
            timestamp: timestamp ?? _nowEpoch,
            currentStatus: status,
          ),
          routeColor: const Color(0xFF0080C0),
          headsign: headsign,
          now: _now,
        ),
      ),
    ),
  );
  await tester.pump();
}

void main() {
  group('formatWait', () {
    test('reads as arriving within half a minute', () {
      expect(formatWait(_nowEpoch + 10, _now), "à l'approche");
      expect(formatWait(_nowEpoch - 60, _now), "à l'approche");
    });

    test('rounds to whole minutes', () {
      expect(formatWait(_nowEpoch + 120, _now), '2 min');
      expect(formatWait(_nowEpoch + 100, _now), '2 min');
    });

    test('switches to hours past an hour', () {
      expect(formatWait(_nowEpoch + 3600, _now), '1 h 00');
      expect(formatWait(_nowEpoch + 3600 + 300, _now), '1 h 05');
    });
  });

  group('vehicle formatting', () {
    test('translates known statuses and falls back otherwise', () {
      expect(vehicleStatusLabel('IN_TRANSIT_TO'), 'En circulation');
      expect(vehicleStatusLabel('STOPPED_AT'), "À l'arrêt");
      expect(vehicleStatusLabel('INCOMING_AT'), "À l'approche");
      expect(vehicleStatusLabel('WHATEVER'), 'Position connue');
    });

    test('maps bearings onto compass points', () {
      expect(compassLabel(0), 'Nord');
      expect(compassLabel(45), 'Nord-Est');
      expect(compassLabel(90), 'Est');
      expect(compassLabel(180), 'Sud');
      expect(compassLabel(270), 'Ouest');
      expect(compassLabel(359), 'Nord');
    });

    test('normalises out-of-range bearings', () {
      expect(compassLabel(720), 'Nord');
      expect(compassLabel(-90), 'Ouest');
    });

    test('converts speed from m/s to km/h', () {
      expect(formatSpeed(0), '0 km/h');
      expect(formatSpeed(10), '36 km/h');
    });

    test('describes how old a position is', () {
      expect(formatAge(_nowEpoch + 5, _now), "à l'instant");
      expect(formatAge(_nowEpoch - 4, _now), 'il y a 4 s');
      expect(formatAge(_nowEpoch - 120, _now), 'il y a 2 min');
      expect(formatAge(_nowEpoch - 7200, _now), 'il y a 2 h');
    });
  });

  group('StopDetailsSheet', () {
    testWidgets('shows the stop name and its departures', (tester) async {
      await _pumpStopSheet(
        tester,
        stop: _stop(),
        repo: FakeStopDepartureRepo(departures: [
          sampleStopDeparture(
            headsign: 'Mosson',
            departureTime: _nowEpoch + 120,
          ),
          sampleStopDeparture(
            tripId: 'trip-2',
            headsign: 'Odysseum',
            departureTime: _nowEpoch + 540,
            isRealtime: false,
          ),
        ]),
      );

      expect(find.text('Comédie'), findsOneWidget);
      expect(find.text('Mosson'), findsOneWidget);
      expect(find.text('2 min'), findsOneWidget);
      expect(find.text('Odysseum'), findsOneWidget);
      expect(find.text('9 min'), findsOneWidget);
    });

    testWidgets('requests departures for the tapped stop', (tester) async {
      final repo = FakeStopDepartureRepo();

      await _pumpStopSheet(tester, stop: _stop(), repo: repo);

      expect(repo.calls, ['s1']);
    });

    testWidgets('shows the platform and code chips when present',
        (tester) async {
      await _pumpStopSheet(
        tester,
        stop: _stop(code: '1234', platformCode: 'B'),
      );

      expect(find.text('Quai B'), findsOneWidget);
      expect(find.text('Code 1234'), findsOneWidget);
    });

    testWidgets('omits chips the feed does not provide', (tester) async {
      await _pumpStopSheet(tester, stop: _stop());

      expect(find.textContaining('Quai'), findsNothing);
      expect(find.textContaining('Code'), findsNothing);
    });

    testWidgets('flags an accessible stop', (tester) async {
      await _pumpStopSheet(tester, stop: _stop(wheelchairBoarding: 1));

      expect(find.text('Accessible'), findsOneWidget);
    });

    testWidgets('flags an inaccessible stop', (tester) async {
      await _pumpStopSheet(tester, stop: _stop(wheelchairBoarding: 2));

      expect(find.text('Non accessible'), findsOneWidget);
    });

    testWidgets('says nothing about accessibility when unknown',
        (tester) async {
      await _pumpStopSheet(tester, stop: _stop(wheelchairBoarding: 0));

      expect(find.text('Accessible'), findsNothing);
      expect(find.text('Non accessible'), findsNothing);
    });

    testWidgets('spins while departures load', (tester) async {
      await _pumpStopSheet(tester, stop: _stop(), load: false);

      expect(find.byType(CircularProgressIndicator), findsOneWidget);
    });

    testWidgets('reports an empty stop', (tester) async {
      await _pumpStopSheet(tester, stop: _stop());

      expect(find.text('Aucun départ prévu.'), findsOneWidget);
    });

    testWidgets('reports a failed lookup', (tester) async {
      await _pumpStopSheet(
        tester,
        stop: _stop(),
        repo: FakeStopDepartureRepo(throwError: true),
      );

      expect(find.text('Départs indisponibles.'), findsOneWidget);
    });

    testWidgets('labels a departure with no headsign', (tester) async {
      await _pumpStopSheet(
        tester,
        stop: _stop(),
        repo: FakeStopDepartureRepo(
          departures: [sampleStopDeparture(headsign: '')],
        ),
      );

      expect(find.text('Direction inconnue'), findsOneWidget);
    });
  });

  group('VehicleDetailsSheet', () {
    testWidgets('leads with the headsign and keeps the id as subtitle',
        (tester) async {
      await _pumpVehicleSheet(tester, headsign: 'Mosson');

      expect(find.text('Mosson'), findsOneWidget);
      expect(find.text('Véhicule v1'), findsOneWidget);
    });

    testWidgets('falls back to the id when no headsign is known',
        (tester) async {
      await _pumpVehicleSheet(tester);

      expect(find.text('Véhicule v1'), findsNWidgets(2));
    });

    testWidgets('falls back when the headsign is blank', (tester) async {
      await _pumpVehicleSheet(tester, headsign: '');

      expect(find.text('Véhicule v1'), findsNWidgets(2));
    });

    testWidgets('shows speed, heading and freshness', (tester) async {
      await _pumpVehicleSheet(
        tester,
        speed: 12,
        bearing: 45,
        timestamp: _nowEpoch - 4,
      );

      expect(find.text('43 km/h'), findsOneWidget);
      expect(find.text('Nord-Est'), findsOneWidget);
      expect(find.text('il y a 4 s'), findsOneWidget);
    });

    testWidgets('shows the status chip', (tester) async {
      await _pumpVehicleSheet(tester, status: 'STOPPED_AT');

      expect(find.text("À l'arrêt"), findsOneWidget);
      expect(find.byIcon(Icons.pause_rounded), findsOneWidget);
    });

    testWidgets('marks a moving vehicle', (tester) async {
      await _pumpVehicleSheet(tester, status: 'IN_TRANSIT_TO');

      expect(find.byIcon(Icons.play_arrow_rounded), findsOneWidget);
    });
  });
}
