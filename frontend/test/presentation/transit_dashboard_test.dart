import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

import 'package:frontend/application/favorites/cubit.dart';
import 'package:frontend/application/route_selection/cubit.dart';
import 'package:frontend/application/vehicle_map/cubit.dart';
import 'package:frontend/presentation/funnel/funnel_page.dart';
import 'package:frontend/presentation/transit_dashboard.dart';
import 'package:frontend/presentation/widgets/top_bar.dart';

import '../helpers/fakes.dart';
import '../helpers/pump.dart';

RouteSelectionCubit _route() => RouteSelectionCubit(
      cityRepo: FakeCityRepo(cities: [sampleCity('Lyon')]),
      conveyanceRepo: FakeConveyanceRepo(conveyances: [sampleConveyance()]),
      stopRepo: FakeStopNameRepo(stops: const ['A', 'B']),
      directionRepo: FakeDirectionRepo(),
      selectionStore: InMemorySelectionStore(),
    );

void main() {
  testWidgets('renders home, ticks the clock, and switches tabs', (tester) async {
    final cubits = TestCubits();
    addTearDown(cubits.close);

    await pumpApp(tester, const TransitDashboard(), cubits: cubits,
        theme: ThemeData(brightness: Brightness.dark));
    await tester.pump();

    expect(find.byType(TopBar), findsOneWidget);

    await tester.pump(const Duration(seconds: 1));

    await tester.tap(find.byIcon(Icons.favorite_rounded));
    await tester.pump();
    await tester.tap(find.byIcon(Icons.home_rounded));
    await tester.pump();

    await tester.pumpWidget(const SizedBox());
  });

  testWidgets('loading a favourite starts watching and returns home',
      (tester) async {
    final favorites =
        FavoritesCubit(store: InMemoryFavoritesStore([sampleSelection()]));
    final harness = StopUpdateHarness();
    final cubits = TestCubits(favorites: favorites, stopUpdate: harness.cubit);
    addTearDown(cubits.close);

    await pumpApp(tester, const TransitDashboard(), cubits: cubits);
    await tester.pump();

    await tester.tap(find.byIcon(Icons.favorite_rounded));
    await tester.pump();
    await tester.tap(find.text('Perrache → Debourg'));
    await tester.pump();

    expect(harness.repo.calls, isNotEmpty);

    harness.cubit.stop();
    cubits.alert.stop();
    await tester.pumpWidget(const SizedBox());
  });

  testWidgets('search opens the funnel and a plain back cancels it',
      (tester) async {
    final route = _route();
    final cubits = TestCubits(routeSelection: route);
    addTearDown(cubits.close);

    await pumpApp(tester, const TransitDashboard(), cubits: cubits);
    await tester.pump();

    await tester.tap(find.byIcon(Icons.search_rounded));
    await pumpFrames(tester);
    expect(find.byType(FunnelPage), findsOneWidget);

    await tester.binding.handlePopRoute();
    await pumpFrames(tester);
    expect(find.byType(FunnelPage), findsNothing);

    await tester.pumpWidget(const SizedBox());
  });

  testWidgets('completing the funnel keeps the selection (no cancel)',
      (tester) async {
    final route = _route();
    final harness = StopUpdateHarness();
    final cubits = TestCubits(routeSelection: route, stopUpdate: harness.cubit);
    addTearDown(cubits.close);

    await pumpApp(tester, const TransitDashboard(), cubits: cubits);
    await tester.pump();

    await tester.tap(find.byIcon(Icons.search_rounded));
    await pumpFrames(tester);
    expect(find.byType(FunnelPage), findsOneWidget);

    await route.loadSelection(sampleSelection());
    await pumpFrames(tester);

    expect(find.byType(FunnelPage), findsNothing);
    expect(harness.repo.calls, isNotEmpty);

    harness.cubit.stop();
    cubits.alert.stop();
    await tester.pumpWidget(const SizedBox());
  });

  testWidgets('the map tab starts watching vehicles for the selection',
      (tester) async {
    final route = _route();
    final vehicles = FakeVehiclePositionRepo();
    final geometry = FakeRouteGeometryRepo();
    final vehicleMap =
        VehicleMapCubit(vehicleRepo: vehicles, geometryRepo: geometry);
    final cubits = TestCubits(routeSelection: route, vehicleMap: vehicleMap);
    addTearDown(cubits.close);

    await setUpAsync(tester, () async {
      await route.loadSelection(sampleSelection());
      return true;
    });

    await pumpApp(tester, const TransitDashboard(), cubits: cubits);
    await tester.pump();

    await tester.tap(find.byIcon(Icons.map_rounded));
    await tester.pump();
    await tester.runAsync(() => Future<void>.delayed(Duration.zero));

    expect(geometry.calls, ['T1']);
    expect(vehicles.calls.single.routeId, 'T1');

    await tester.pumpWidget(const SizedBox());
  });

  testWidgets('the map tab does nothing without a complete selection',
      (tester) async {
    final geometry = FakeRouteGeometryRepo();
    final vehicleMap = VehicleMapCubit(
      vehicleRepo: FakeVehiclePositionRepo(),
      geometryRepo: geometry,
    );
    final cubits = TestCubits(vehicleMap: vehicleMap);
    addTearDown(cubits.close);

    await pumpApp(tester, const TransitDashboard(), cubits: cubits);
    await tester.pump();

    await tester.tap(find.byIcon(Icons.map_rounded));
    await tester.pump();

    expect(geometry.calls, isEmpty);

    await tester.pumpWidget(const SizedBox());
  });
}
