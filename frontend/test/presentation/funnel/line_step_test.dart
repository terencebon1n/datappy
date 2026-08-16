import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

import 'package:frontend/application/nearby/cubit.dart';
import 'package:frontend/application/route_selection/cubit.dart';
import 'package:frontend/application/route_selection/state.dart';
import 'package:frontend/presentation/funnel/funnel_widgets.dart';
import 'package:frontend/presentation/funnel/line_step.dart';

import '../../helpers/fakes.dart';
import '../../helpers/pump.dart';

Future<RouteSelectionCubit> _atLineStep(
  WidgetTester tester, {
  required List conveyances,
}) =>
    setUpAsync(tester, () async {
      final cubit = RouteSelectionCubit(
        cityRepo: FakeCityRepo(cities: [sampleCity('Lyon')]),
        conveyanceRepo: FakeConveyanceRepo(conveyances: conveyances.cast()),
        stopRepo: FakeStopNameRepo(stops: const ['A', 'B']),
        directionRepo: FakeDirectionRepo(),
        selectionStore: InMemorySelectionStore(),
      );
      await Future<void>.delayed(Duration.zero);
      cubit.selectCity(sampleCity('Lyon'));
      await Future<void>.delayed(Duration.zero);
      return cubit;
    });

void main() {
  testWidgets('shows a spinner while conveyances are empty', (tester) async {
    final route = await _atLineStep(tester, conveyances: const []);
    final cubits = TestCubits(routeSelection: route);
    addTearDown(cubits.close);

    await pumpApp(tester, const Scaffold(body: LineStep()), cubits: cubits);
    await tester.pump();

    expect(find.byType(CircularProgressIndicator), findsOneWidget);
  });

  testWidgets('groups conveyances by type and advances on tap', (tester) async {
    final route = await _atLineStep(tester, conveyances: [
      sampleConveyance(id: 'T1', typeName: 'Tramway', typeId: 0),
      sampleConveyance(id: 'B9', typeName: 'Bus', typeId: 3),
    ]);
    final cubits = TestCubits(routeSelection: route);
    addTearDown(cubits.close);

    await pumpApp(tester, const Scaffold(body: LineStep()), cubits: cubits);
    await tester.pump();

    expect(find.text('TRAMWAY'), findsOneWidget);
    expect(find.text('BUS'), findsOneWidget);
    expect(find.byType(RouteListTile), findsNWidgets(2));

    await tester.tap(find.text('T1 - Tram T1: Perrache - Debourg').first);
    await tester.pump();

    expect(route.state.step, FunnelStep.source);
    expect(route.state.stops, const ['A', 'B']);
  });

  testWidgets('the nearby entry starts a lookup and opens the nearby step',
      (tester) async {
    final route = await _atLineStep(tester, conveyances: [sampleConveyance()]);
    final repo = FakeNearbyStopRepo(stops: [sampleNearbyStop()]);
    final nearby = NearbyCubit(
      nearbyRepo: repo,
      location: FakeLocationProvider(),
    );
    final cubits = TestCubits(routeSelection: route, nearby: nearby);
    addTearDown(cubits.close);

    await pumpApp(tester, const Scaffold(body: LineStep()), cubits: cubits);
    await tester.pump();

    await tester.tap(find.text('Autour de moi'));
    await tester.pump();

    expect(route.state.step, FunnelStep.nearby);
    await tester.runAsync(() => Future<void>.delayed(Duration.zero));
    expect(repo.calls, hasLength(1));
  });
}
