import 'dart:async';

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

import 'package:frontend/application/route_selection/cubit.dart';
import 'package:frontend/application/route_selection/state.dart';
import 'package:frontend/presentation/funnel/stop_step.dart';

import '../../helpers/fakes.dart';
import '../../helpers/pump.dart';

Future<RouteSelectionCubit> _atSource(
  WidgetTester tester, {
  required List<String> stops,
  FakeDirectionRepo? directionRepo,
}) =>
    setUpAsync(tester, () async {
      final cubit = RouteSelectionCubit(
        cityRepo: FakeCityRepo(cities: [sampleCity('Lyon')]),
        conveyanceRepo: FakeConveyanceRepo(conveyances: [sampleConveyance()]),
        stopRepo: FakeStopNameRepo(stops: stops),
        directionRepo: directionRepo ?? FakeDirectionRepo(),
        selectionStore: InMemorySelectionStore(),
      );
      await Future<void>.delayed(Duration.zero);
      cubit.selectCity(sampleCity('Lyon'));
      await Future<void>.delayed(Duration.zero);
      cubit.selectConveyance(sampleConveyance());
      await Future<void>.delayed(Duration.zero);
      return cubit;
    });

void main() {
  testWidgets('source shows a spinner until stops arrive', (tester) async {
    final route = await _atSource(tester, stops: const []);
    final cubits = TestCubits(routeSelection: route);
    addTearDown(cubits.close);

    await pumpApp(tester, const Scaffold(body: StopStep(isSource: true)), cubits: cubits);
    await tester.pump();

    expect(find.byType(CircularProgressIndicator), findsOneWidget);
  });

  testWidgets('source lists stops, filters them, and advances on tap',
      (tester) async {
    final route =
        await _atSource(tester, stops: const ['Perrache', 'Debourg', 'Bellecour']);
    final cubits = TestCubits(routeSelection: route);
    addTearDown(cubits.close);

    await pumpApp(tester, const Scaffold(body: StopStep(isSource: true)), cubits: cubits);
    await tester.pump();

    expect(find.text('Arrêt de départ'), findsOneWidget);
    expect(find.text('Bellecour'), findsOneWidget);

    await tester.enterText(find.byType(TextField), 'bel');
    await tester.pump();
    expect(find.text('Perrache'), findsNothing);
    expect(find.text('Bellecour'), findsOneWidget);

    await tester.enterText(find.byType(TextField), 'zzz');
    await tester.pump();
    expect(find.text('Aucun arrêt trouvé'), findsOneWidget);

    await tester.enterText(find.byType(TextField), '');
    await tester.pump();
    await tester.tap(find.text('Perrache'));
    await tester.pump();

    expect(route.state.step, FunnelStep.dest);
  });

  testWidgets('the back button returns to the previous step', (tester) async {
    final route = await _atSource(tester, stops: const ['Perrache']);
    final cubits = TestCubits(routeSelection: route);
    addTearDown(cubits.close);

    await pumpApp(tester, const Scaffold(body: StopStep(isSource: true)), cubits: cubits);
    await tester.pump();

    await tester.tap(find.byIcon(Icons.arrow_back));
    await tester.pump();

    expect(route.state.step, FunnelStep.line);
  });

  testWidgets('dest hides the source, shows the resolving overlay, then clears it',
      (tester) async {
    final gate = Completer<void>();
    final route = await _atSource(
      tester,
      stops: const ['Perrache', 'Debourg'],
      directionRepo: FakeDirectionRepo(gate: gate.future),
    );
    route.selectSourceStop('Perrache');
    final cubits = TestCubits(routeSelection: route);
    addTearDown(cubits.close);

    await pumpApp(tester, const Scaffold(body: StopStep(isSource: false)), cubits: cubits);
    await tester.pump();

    expect(find.text("Arrêt d'arrivée"), findsOneWidget);
    expect(find.text('Perrache'), findsNothing);
    expect(find.text('Départ · Perrache'), findsOneWidget);

    await tester.tap(find.text('Debourg'));
    await tester.pump();
    expect(find.text('Recherche des horaires…'), findsOneWidget);

    gate.complete();
    await tester.pump();
    await tester.pump();

    expect(find.text('Recherche des horaires…'), findsNothing);
    expect(route.state.direction, isNotNull);
    expect(route.state.destStop, 'Debourg');
  });
}
