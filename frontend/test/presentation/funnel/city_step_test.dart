import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

import 'package:frontend/application/route_selection/cubit.dart';
import 'package:frontend/application/route_selection/state.dart';
import 'package:frontend/presentation/funnel/city_step.dart';

import '../../helpers/fakes.dart';
import '../../helpers/pump.dart';

Future<RouteSelectionCubit> _route(WidgetTester tester, {required List cities}) =>
    setUpAsync(tester, () async {
      final cubit = RouteSelectionCubit(
        cityRepo: FakeCityRepo(cities: cities.cast()),
        conveyanceRepo: FakeConveyanceRepo(conveyances: [sampleConveyance()]),
        stopRepo: FakeStopNameRepo(),
        directionRepo: FakeDirectionRepo(),
        selectionStore: InMemorySelectionStore(),
      );
      await Future<void>.delayed(Duration.zero);
      return cubit;
    });

void main() {
  testWidgets('shows a spinner while cities are empty', (tester) async {
    final route = await _route(tester, cities: const []);
    final cubits = TestCubits(routeSelection: route);
    addTearDown(cubits.close);

    await pumpApp(tester, const Scaffold(body: CityStep()), cubits: cubits);
    await tester.pump();

    expect(find.byType(CircularProgressIndicator), findsOneWidget);
  });

  testWidgets('lists cities (capitalizing) and advances on tap', (tester) async {
    final route = await _route(tester, cities: [sampleCity(''), sampleCity('lyon')]);
    final cubits = TestCubits(routeSelection: route);
    addTearDown(cubits.close);

    await pumpApp(tester, const Scaffold(body: CityStep()), cubits: cubits);
    await tester.pump();

    expect(find.text('Lyon'), findsOneWidget);

    await tester.tap(find.text('Lyon'));
    await tester.pump();

    expect(route.state.step, FunnelStep.line);
    expect(route.state.conveyances, isNotEmpty);
  });

  testWidgets('the close button attempts to pop', (tester) async {
    final route = await _route(tester, cities: [sampleCity('lyon')]);
    final cubits = TestCubits(routeSelection: route);
    addTearDown(cubits.close);

    await pumpApp(tester, const Scaffold(body: CityStep()), cubits: cubits);
    await tester.pump();

    await tester.tap(find.byIcon(Icons.close));
    await tester.pump();
  });
}
