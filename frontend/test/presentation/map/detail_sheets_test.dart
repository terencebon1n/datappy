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
      () => cubit.load(stopId: 's1', city: sampleCity()),
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

  group('buildDepartureColumns', () {
    test('one column per destination', () {
      final columns = buildDepartureColumns([
        sampleStopDeparture(tripId: 'a', headsign: 'Mosson'),
        sampleStopDeparture(tripId: 'b', headsign: 'Odysseum'),
        sampleStopDeparture(tripId: 'c', headsign: 'Mosson'),
      ]);

      expect(columns.map((c) => c.destination), ['Mosson', 'Odysseum']);
      expect(columns.first.departures, hasLength(2));
    });

    test('never mixes transit types into one column', () {
      final columns = buildDepartureColumns([
        sampleStopDeparture(tripId: 'tram', routeTypeId: 0, headsign: 'Gare'),
        sampleStopDeparture(tripId: 'bus', routeTypeId: 3, headsign: 'Gare'),
      ]);

      expect(columns, hasLength(2));
      expect(columns.map((c) => c.routeTypeId), [0, 3]);
      expect(columns.every((c) => c.destination == 'Gare'), isTrue);
      expect(columns.first.departures.single.tripId, 'tram');
      expect(columns.last.departures.single.tripId, 'bus');
    });

    test('keeps transit types together, soonest first within a type', () {
      final columns = buildDepartureColumns([
        sampleStopDeparture(
          tripId: 'bus-early',
          routeTypeId: 3,
          headsign: 'Jacou',
          departureTime: _nowEpoch + 60,
        ),
        sampleStopDeparture(
          tripId: 'tram-late',
          routeTypeId: 0,
          headsign: 'Mosson',
          departureTime: _nowEpoch + 900,
        ),
        sampleStopDeparture(
          tripId: 'tram-soon',
          routeTypeId: 0,
          headsign: 'Odysseum',
          departureTime: _nowEpoch + 300,
        ),
      ]);

      expect(
        columns.map((c) => c.destination),
        ['Odysseum', 'Mosson', 'Jacou'],
      );
    });

    test('sorts each column by departure time', () {
      final columns = buildDepartureColumns([
        sampleStopDeparture(tripId: 'late', departureTime: _nowEpoch + 600),
        sampleStopDeparture(tripId: 'soon', departureTime: _nowEpoch + 60),
      ]);

      expect(columns.single.departures.map((d) => d.tripId), ['soon', 'late']);
    });

    test('labels a missing headsign', () {
      final columns = buildDepartureColumns([sampleStopDeparture(headsign: '')]);

      expect(columns.single.destination, 'Direction inconnue');
    });

    test('yields nothing for no departures', () {
      expect(buildDepartureColumns([]), isEmpty);
    });
  });

  group('StopDetailsSheet columns', () {
    testWidgets('shows one column per destination with times stacked',
        (tester) async {
      await _pumpStopSheet(
        tester,
        stop: _stop(),
        repo: FakeStopDepartureRepo(departures: [
          sampleStopDeparture(
            tripId: 'a',
            headsign: 'Mosson',
            departureTime: _nowEpoch + 120,
          ),
          sampleStopDeparture(
            tripId: 'b',
            headsign: 'Mosson',
            departureTime: _nowEpoch + 540,
          ),
          sampleStopDeparture(
            tripId: 'c',
            directionId: 1,
            headsign: 'Odysseum',
            departureTime: _nowEpoch + 240,
          ),
          sampleStopDeparture(
            tripId: 'd',
            directionId: 1,
            headsign: 'Odysseum',
            departureTime: _nowEpoch + 720,
          ),
        ]),
      );

      expect(find.text('Mosson'), findsOneWidget);
      expect(find.text('Odysseum'), findsOneWidget);
      expect(find.text('2 min'), findsOneWidget);
      expect(find.text('9 min'), findsOneWidget);
      expect(find.text('4 min'), findsOneWidget);
      expect(find.text('12 min'), findsOneWidget);
    });

    testWidgets('separates the columns with a divider', (tester) async {
      await _pumpStopSheet(
        tester,
        stop: _stop(),
        repo: FakeStopDepartureRepo(departures: [
          sampleStopDeparture(headsign: 'Mosson'),
          sampleStopDeparture(
            tripId: 'b',
            directionId: 1,
            headsign: 'Odysseum',
          ),
        ]),
      );

      expect(find.byType(VerticalDivider), findsOneWidget);
    });

    testWidgets('a single destination needs no divider', (tester) async {
      await _pumpStopSheet(
        tester,
        stop: _stop(),
        repo: FakeStopDepartureRepo(
          departures: [sampleStopDeparture(headsign: 'Mosson')],
        ),
      );

      expect(find.text('Mosson'), findsOneWidget);
      expect(find.byType(VerticalDivider), findsNothing);
    });

    testWidgets('renders three destinations when the route branches',
        (tester) async {
      await _pumpStopSheet(
        tester,
        stop: _stop(),
        repo: FakeStopDepartureRepo(departures: [
          sampleStopDeparture(tripId: 'a', headsign: 'Mosson'),
          sampleStopDeparture(tripId: 'b', headsign: 'Odysseum'),
          sampleStopDeparture(tripId: 'c', headsign: 'Jacou'),
        ]),
      );

      expect(find.byType(VerticalDivider), findsNWidgets(2));
      expect(find.text('Jacou'), findsOneWidget);
    });
  });

  group('StopDetailsSheet across lines', () {
    testWidgets('badges each departure with its line', (tester) async {
      await _pumpStopSheet(
        tester,
        stop: _stop(),
        repo: FakeStopDepartureRepo(departures: [
          sampleStopDeparture(
            tripId: 'a',
            routeId: 'T1',
            routeShortName: '1',
            headsign: 'Mosson',
            departureTime: _nowEpoch + 120,
          ),
          sampleStopDeparture(
            tripId: 'b',
            routeId: 'B9',
            routeShortName: '9',
            headsign: 'Jacou',
            departureTime: _nowEpoch + 300,
          ),
        ]),
      );

      expect(find.text('1'), findsOneWidget);
      expect(find.text('9'), findsOneWidget);
      expect(find.text('Mosson'), findsOneWidget);
      expect(find.text('Jacou'), findsOneWidget);
    });

    testWidgets('two lines sharing a destination share one column',
        (tester) async {
      await _pumpStopSheet(
        tester,
        stop: _stop(),
        repo: FakeStopDepartureRepo(departures: [
          sampleStopDeparture(
            tripId: 'a',
            routeId: 'T1',
            routeShortName: '1',
            headsign: 'Gare',
            departureTime: _nowEpoch + 120,
          ),
          sampleStopDeparture(
            tripId: 'b',
            routeId: 'T4',
            routeShortName: '4',
            headsign: 'Gare',
            departureTime: _nowEpoch + 300,
          ),
        ]),
      );

      expect(find.text('Gare'), findsOneWidget);
      expect(find.byType(VerticalDivider), findsNothing);
      expect(find.text('1'), findsOneWidget);
      expect(find.text('4'), findsOneWidget);
    });

    testWidgets('a line with no colour still badges', (tester) async {
      await _pumpStopSheet(
        tester,
        stop: _stop(),
        repo: FakeStopDepartureRepo(departures: [
          sampleStopDeparture(routeShortName: '7', routeColorValue: null),
        ]),
      );

      expect(find.text('7'), findsOneWidget);
    });

    testWidgets('a line with no short name badges a placeholder',
        (tester) async {
      await _pumpStopSheet(
        tester,
        stop: _stop(),
        repo: FakeStopDepartureRepo(
          departures: [sampleStopDeparture(routeShortName: '')],
        ),
      );

      expect(find.text('?'), findsOneWidget);
    });
  });

  group('StopDetailsSheet scrolling', () {
    testWidgets('scrolls horizontally when the columns overflow',
        (tester) async {
      await _pumpStopSheet(
        tester,
        stop: _stop(),
        repo: FakeStopDepartureRepo(departures: [
          for (var i = 0; i < 6; i++)
            sampleStopDeparture(
              tripId: 'trip-$i',
              routeShortName: '$i',
              headsign: 'Destination $i',
              departureTime: _nowEpoch + 60 * (i + 1),
            ),
        ]),
      );

      final scroller = tester.widget<SingleChildScrollView>(
        find.byType(SingleChildScrollView),
      );
      expect(scroller.scrollDirection, Axis.horizontal);

      expect(find.text('Destination 0'), findsOneWidget);
      await tester.drag(
        find.byType(SingleChildScrollView),
        const Offset(-400, 0),
      );
      await tester.pump();

      expect(find.text('Destination 5'), findsOneWidget);
    });

    testWidgets('gives every column the same width', (tester) async {
      await _pumpStopSheet(
        tester,
        stop: _stop(),
        repo: FakeStopDepartureRepo(departures: [
          sampleStopDeparture(tripId: 'a', headsign: 'Mosson'),
          sampleStopDeparture(tripId: 'b', headsign: 'Odysseum'),
        ]),
      );

      final widths = tester
          .widgetList<SizedBox>(find.byType(SizedBox))
          .where((box) => box.width == departureColumnWidth);

      expect(widths, hasLength(2));
    });

    testWidgets('a tram and a bus to the same place get separate columns',
        (tester) async {
      await _pumpStopSheet(
        tester,
        stop: _stop(),
        repo: FakeStopDepartureRepo(departures: [
          sampleStopDeparture(
            tripId: 'tram',
            routeTypeId: 0,
            routeShortName: '1',
            headsign: 'Gare',
          ),
          sampleStopDeparture(
            tripId: 'bus',
            routeTypeId: 3,
            routeShortName: '9',
            headsign: 'Gare',
          ),
        ]),
      );

      expect(find.text('Gare'), findsNWidgets(2));
      expect(find.byIcon(Icons.tram), findsOneWidget);
      expect(find.byIcon(Icons.directions_bus), findsOneWidget);
      expect(find.byType(VerticalDivider), findsOneWidget);
    });
  });
}
