import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

import 'package:frontend/application/route_selection/cubit.dart';
import 'package:frontend/application/route_selection/state.dart';
import 'package:frontend/presentation/funnel/city_step.dart';
import 'package:frontend/presentation/funnel/funnel_page.dart';
import 'package:frontend/presentation/funnel/line_step.dart';
import 'package:frontend/presentation/funnel/stop_step.dart';

import '../../helpers/fakes.dart';
import '../../helpers/pump.dart';

Future<RouteSelectionCubit> _route(WidgetTester tester) =>
    setUpAsync(tester, () async {
      final cubit = RouteSelectionCubit(
        cityRepo: FakeCityRepo(cities: [sampleCity('Lyon')]),
        conveyanceRepo: FakeConveyanceRepo(conveyances: [sampleConveyance()]),
        stopRepo: FakeStopNameRepo(stops: const ['A', 'B']),
        directionRepo: FakeDirectionRepo(),
        selectionStore: InMemorySelectionStore(),
      );
      await Future<void>.delayed(Duration.zero);
      return cubit;
    });

Widget _opener() => Builder(
      builder: (context) => TextButton(
        onPressed: () => Navigator.of(context).push(
          MaterialPageRoute<bool>(builder: (_) => const FunnelPage()),
        ),
        child: const Text('open'),
      ),
    );

void main() {
  testWidgets('renders the source and destination stop steps', (tester) async {
    final route = await _route(tester);
    await tester.runAsync(() async {
      route.selectCity(sampleCity('Lyon'));
      await Future<void>.delayed(Duration.zero);
      route.selectConveyance(sampleConveyance());
      await Future<void>.delayed(Duration.zero);
    });
    final cubits = TestCubits(routeSelection: route);
    addTearDown(cubits.close);

    await pumpApp(tester, _opener(), cubits: cubits);
    await tester.tap(find.text('open'));
    await tester.pumpAndSettle();
    expect(route.state.step, FunnelStep.source);
    expect(find.byType(StopStep), findsOneWidget);

    route.selectSourceStop('A');
    await tester.pumpAndSettle();
    expect(route.state.step, FunnelStep.dest);
    expect(find.byType(StopStep), findsOneWidget);
  });

  testWidgets('renders the active step and walks back through PopScope',
      (tester) async {
    final route = await _route(tester);
    await tester.runAsync(() async {
      route.selectCity(sampleCity('Lyon'));
      await Future<void>.delayed(Duration.zero);
    });
    final cubits = TestCubits(routeSelection: route);
    addTearDown(cubits.close);

    await pumpApp(tester, _opener(), cubits: cubits);
    await tester.tap(find.text('open'));
    await tester.pumpAndSettle();
    expect(find.byType(LineStep), findsOneWidget);

    await tester.binding.handlePopRoute();
    await tester.pumpAndSettle();
    expect(route.state.step, FunnelStep.city);
    expect(find.byType(CityStep), findsOneWidget);

    await tester.binding.handlePopRoute();
    await tester.pumpAndSettle();
    expect(find.byType(FunnelPage), findsNothing);
  });

  testWidgets('auto-submits and pops once the selection is complete',
      (tester) async {
    final route = await _route(tester);
    final harness = StopUpdateHarness();
    final cubits = TestCubits(routeSelection: route, stopUpdate: harness.cubit);
    addTearDown(cubits.close);

    await pumpApp(tester, _opener(), cubits: cubits);
    await tester.tap(find.text('open'));
    await tester.pumpAndSettle();
    expect(find.byType(FunnelPage), findsOneWidget);

    await route.loadSelection(sampleSelection());
    await tester.pumpAndSettle();

    expect(find.byType(FunnelPage), findsNothing);
    expect(harness.repo.calls, isNotEmpty);
    harness.cubit.stop();
    cubits.alert.stop();
  });

  testWidgets('does not submit while another route sits on top', (tester) async {
    final route = await _route(tester);
    final harness = StopUpdateHarness();
    final cubits = TestCubits(routeSelection: route, stopUpdate: harness.cubit);
    addTearDown(cubits.close);

    await pumpApp(tester, _opener(), cubits: cubits);
    await tester.tap(find.text('open'));
    await tester.pumpAndSettle();

    final navigator = tester.state<NavigatorState>(find.byType(Navigator).first);
    navigator.push(MaterialPageRoute<void>(
      builder: (_) => const Scaffold(body: Text('on-top')),
    ));
    await tester.pumpAndSettle();
    expect(find.text('on-top'), findsOneWidget);

    await route.loadSelection(sampleSelection());
    await tester.pumpAndSettle();

    expect(harness.repo.calls, isEmpty);
    expect(find.text('on-top'), findsOneWidget);
  });
}
