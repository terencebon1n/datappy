import 'dart:async';

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

import 'package:frontend/application/nearby/cubit.dart';
import 'package:frontend/application/route_selection/cubit.dart';
import 'package:frontend/application/route_selection/state.dart';
import 'package:frontend/domain/repositories/i_location.dart';
import 'package:frontend/presentation/funnel/funnel_widgets.dart';
import 'package:frontend/presentation/funnel/nearby_step.dart';

import '../../helpers/fakes.dart';
import '../../helpers/pump.dart';

Future<RouteSelectionCubit> _atNearbyStep(WidgetTester tester) =>
    setUpAsync(tester, () async {
      final cubit = RouteSelectionCubit(
        cityRepo: FakeCityRepo(cities: [sampleCity('Montpellier')]),
        conveyanceRepo: FakeConveyanceRepo(),
        stopRepo: FakeStopNameRepo(stops: const ['A', 'B']),
        directionRepo: FakeDirectionRepo(),
        selectionStore: InMemorySelectionStore(),
      );
      await Future<void>.delayed(Duration.zero);
      cubit.selectCity(sampleCity('Montpellier'));
      await Future<void>.delayed(Duration.zero);
      cubit.browseNearby();
      return cubit;
    });

Future<TestCubits> _pump(
  WidgetTester tester, {
  required NearbyCubit nearby,
  RouteSelectionCubit? route,
}) async {
  final cubits = TestCubits(routeSelection: route, nearby: nearby);
  addTearDown(cubits.close);
  await pumpApp(tester, Scaffold(body: NearbyStep()), cubits: cubits);
  await tester.pump();
  return cubits;
}

void main() {
  test('formats distances below and above a kilometre', () {
    expect(formatDistance(124), '124 m');
    expect(formatDistance(999), '999 m');
    expect(formatDistance(1000), '1.0 km');
    expect(formatDistance(2350), '2.4 km');
  });

  testWidgets('shows the city and title in the header', (tester) async {
    final route = await _atNearbyStep(tester);
    final nearby = NearbyCubit(
      nearbyRepo: FakeNearbyStopRepo(),
      location: FakeLocationProvider(),
    );

    await _pump(tester, nearby: nearby, route: route);

    expect(find.text('MONTPELLIER'), findsOneWidget);
    expect(find.text('Autour de moi'), findsOneWidget);
  });

  testWidgets('shows a locating spinner while the position is read',
      (tester) async {
    final gate = Completer<void>();
    final nearby = NearbyCubit(
      nearbyRepo: FakeNearbyStopRepo(),
      location: FakeLocationProvider(gate: gate.future),
    );
    nearby.findNearby(sampleCity());

    await _pump(tester, nearby: nearby);

    expect(find.byType(CircularProgressIndicator), findsOneWidget);
    expect(find.text('Localisation en cours…'), findsOneWidget);

    gate.complete();
    await tester.pumpAndSettle();
  });

  testWidgets('shows a loading spinner while stops are fetched',
      (tester) async {
    final gate = Completer<void>();
    final nearby = NearbyCubit(
      nearbyRepo: FakeNearbyStopRepo(gate: gate.future),
      location: FakeLocationProvider(),
    );
    nearby.findNearby(sampleCity());
    await tester.runAsync(() => Future<void>.delayed(Duration.zero));

    await _pump(tester, nearby: nearby);

    expect(find.text('Recherche des arrêts…'), findsOneWidget);

    gate.complete();
    await tester.pumpAndSettle();
  });

  testWidgets('lists nearby stops with their distance and lines',
      (tester) async {
    final nearby = NearbyCubit(
      nearbyRepo: FakeNearbyStopRepo(stops: [
        sampleNearbyStop(
          name: 'Comédie',
          distanceMeters: 124,
          routes: [
            sampleConveyance(id: 'T1', shortName: '1'),
            sampleConveyance(id: 'T4', shortName: '4'),
          ],
        ),
        sampleNearbyStop(name: 'Gare', distanceMeters: 1250),
      ]),
      location: FakeLocationProvider(),
    );
    await tester.runAsync(() => nearby.findNearby(sampleCity()));

    await _pump(tester, nearby: nearby);

    expect(find.text('ARRÊTS LES PLUS PROCHES'), findsOneWidget);
    expect(find.text('Comédie'), findsOneWidget);
    expect(find.text('124 m'), findsOneWidget);
    expect(find.text('Gare'), findsOneWidget);
    expect(find.text('1.3 km'), findsOneWidget);
    expect(find.byType(RouteBadge), findsNWidgets(3));
  });

  testWidgets('tapping a line selects it as the source and advances',
      (tester) async {
    final route = await _atNearbyStep(tester);
    final nearby = NearbyCubit(
      nearbyRepo: FakeNearbyStopRepo(stops: [
        sampleNearbyStop(
          name: 'Comédie',
          routes: [sampleConveyance(id: 'T1', shortName: '1')],
        ),
      ]),
      location: FakeLocationProvider(),
    );
    await tester.runAsync(() => nearby.findNearby(sampleCity()));

    await _pump(tester, nearby: nearby, route: route);
    await tester.tap(find.byType(RouteListTile));
    await tester.pump();

    expect(route.state.step, FunnelStep.dest);
    expect(route.state.sourceStop, 'Comédie');
    expect(route.state.selectedConveyance?.id, 'T1');
    expect(route.state.stops, const ['A', 'B']);
  });

  testWidgets('tapping the row label, not just the badge, selects the line',
      (tester) async {
    final route = await _atNearbyStep(tester);
    final nearby = NearbyCubit(
      nearbyRepo: FakeNearbyStopRepo(stops: [
        sampleNearbyStop(
          name: 'Comédie',
          routes: [sampleConveyance(id: 'T1', shortName: '1')],
        ),
      ]),
      location: FakeLocationProvider(),
    );
    await tester.runAsync(() => nearby.findNearby(sampleCity()));

    await _pump(tester, nearby: nearby, route: route);
    await tester.tap(find.text('T1 - Tram T1: Perrache - Debourg'));
    await tester.pump();

    expect(route.state.step, FunnelStep.dest);
    expect(route.state.selectedConveyance?.id, 'T1');
  });

  testWidgets('each line of a multi-line stop is its own tappable row',
      (tester) async {
    final route = await _atNearbyStep(tester);
    final nearby = NearbyCubit(
      nearbyRepo: FakeNearbyStopRepo(stops: [
        sampleNearbyStop(
          name: 'Comédie',
          routes: [
            sampleConveyance(id: 'T1', shortName: '1'),
            sampleConveyance(id: 'T4', shortName: '4'),
          ],
        ),
      ]),
      location: FakeLocationProvider(),
    );
    await tester.runAsync(() => nearby.findNearby(sampleCity()));

    await _pump(tester, nearby: nearby, route: route);
    expect(find.byType(RouteListTile), findsNWidgets(2));

    await tester.tap(find.byType(RouteListTile).last);
    await tester.pump();

    expect(route.state.selectedConveyance?.id, 'T4');
    expect(route.state.sourceStop, 'Comédie');
  });

  testWidgets('explains a refused permission', (tester) async {
    final nearby = NearbyCubit(
      nearbyRepo: FakeNearbyStopRepo(),
      location:
          FakeLocationProvider(permission: LocationPermissionStatus.denied),
    );
    await tester.runAsync(() => nearby.findNearby(sampleCity()));

    await _pump(tester, nearby: nearby);

    expect(find.textContaining('Autorisez la localisation'), findsOneWidget);
  });

  testWidgets('explains a disabled location service', (tester) async {
    final nearby = NearbyCubit(
      nearbyRepo: FakeNearbyStopRepo(),
      location: FakeLocationProvider(
        permission: LocationPermissionStatus.serviceDisabled,
      ),
    );
    await tester.runAsync(() => nearby.findNearby(sampleCity()));

    await _pump(tester, nearby: nearby);

    expect(find.textContaining('localisation est désactivée'), findsOneWidget);
  });

  testWidgets('reports a failed lookup', (tester) async {
    final nearby = NearbyCubit(
      nearbyRepo: FakeNearbyStopRepo(throwError: true),
      location: FakeLocationProvider(),
    );
    await tester.runAsync(() => nearby.findNearby(sampleCity()));

    await _pump(tester, nearby: nearby);

    expect(find.text('Impossible de récupérer les arrêts proches.'),
        findsOneWidget);
  });

  testWidgets('reports an empty result', (tester) async {
    final nearby = NearbyCubit(
      nearbyRepo: FakeNearbyStopRepo(),
      location: FakeLocationProvider(),
    );
    await tester.runAsync(() => nearby.findNearby(sampleCity()));

    await _pump(tester, nearby: nearby);

    expect(find.text('Aucun arrêt à proximité.'), findsOneWidget);
  });

  testWidgets('going back returns to the line step', (tester) async {
    final route = await _atNearbyStep(tester);
    final nearby = NearbyCubit(
      nearbyRepo: FakeNearbyStopRepo(),
      location: FakeLocationProvider(),
    );

    await _pump(tester, nearby: nearby, route: route);
    await tester.tap(find.byIcon(Icons.arrow_back));
    await tester.pump();

    expect(route.state.step, FunnelStep.line);
  });
}
