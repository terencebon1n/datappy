import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

import 'package:frontend/application/route_selection/cubit.dart';
import 'package:frontend/domain/saved_selection.dart';
import 'package:frontend/presentation/widgets/line_card.dart';

import '../../helpers/fakes.dart';
import '../../helpers/pump.dart';

final _now = DateTime(2020, 1, 1, 8, 5, 3);

RouteSelectionCubit _emptyRoute() => RouteSelectionCubit(
      cityRepo: FakeCityRepo(),
      conveyanceRepo: FakeConveyanceRepo(),
      stopRepo: FakeStopNameRepo(),
      directionRepo: FakeDirectionRepo(),
      selectionStore: InMemorySelectionStore(),
    );

Future<RouteSelectionCubit> _routeWith(int color, {String longName = 'Tram 1'}) async {
  final cubit = _emptyRoute();
  await cubit.loadSelection(SavedSelection(
    city: sampleCity(),
    conveyance: sampleConveyance(colorValue: color, longName: longName),
    sourceStop: 'Perrache',
    destStop: 'Debourg',
    direction: sampleDirection(),
  ));
  return cubit;
}

void main() {
  testWidgets('no line selected: dash badge and placeholder destination',
      (tester) async {
    final cubits = TestCubits();
    addTearDown(cubits.close);

    await pumpApp(tester, LineCard(now: _now), cubits: cubits);
    await tester.pump();

    expect(find.text('—'), findsOneWidget);
    expect(find.textContaining('Destination non sélectionnée'), findsOneWidget);

    await tester.pumpWidget(const SizedBox());
  });

  testWidgets('dark line colour uses white badge text and shows the via line',
      (tester) async {
    final route = await _routeWith(0xFF0080C0);
    final cubits = TestCubits(routeSelection: route);
    addTearDown(cubits.close);

    await pumpApp(tester, LineCard(now: _now), cubits: cubits);
    await tester.pump();

    expect(find.text('T1'), findsOneWidget);
    expect(find.textContaining('Debourg'), findsOneWidget);
    expect(find.text('Tram 1'), findsOneWidget);

    await tester.pumpWidget(const SizedBox());
  });

  testWidgets('near-white line colour falls back to the accent badge',
      (tester) async {
    final route = await _routeWith(0xFFFFFFFF, longName: '');
    final cubits = TestCubits(routeSelection: route);
    addTearDown(cubits.close);

    await pumpApp(tester, LineCard(now: _now), cubits: cubits);
    await tester.pump();

    expect(find.text('T1'), findsOneWidget);
    expect(find.text('Tram 1'), findsNothing);

    await tester.pumpWidget(const SizedBox());
  });

  testWidgets('mid-light line colour uses dark badge text', (tester) async {
    final route = await _routeWith(0xFFCCCCCC);
    final cubits = TestCubits(routeSelection: route);
    addTearDown(cubits.close);

    await pumpApp(tester, LineCard(now: _now), cubits: cubits);
    await tester.pump();

    expect(find.text('T1'), findsOneWidget);

    await tester.pumpWidget(const SizedBox());
  });

  testWidgets('live feed reveals the running clock', (tester) async {
    final harness = StopUpdateHarness();
    final cubits = TestCubits(stopUpdate: harness.cubit);
    addTearDown(cubits.close);

    harness.live(const []);
    await pumpApp(tester, LineCard(now: _now), cubits: cubits);
    await tester.pump();
    await tester.pump();

    expect(find.text('08:05:03'), findsOneWidget);

    harness.cubit.stop();
    await tester.pumpWidget(const SizedBox());
  });
}
