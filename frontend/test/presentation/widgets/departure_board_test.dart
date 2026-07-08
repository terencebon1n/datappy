import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

import 'package:frontend/presentation/widgets/departure_board.dart';
import 'package:frontend/presentation/widgets/departure_row.dart';

import '../../helpers/fakes.dart';
import '../../helpers/pump.dart';

Widget _board() => DepartureBoard(now: DateTime.fromMillisecondsSinceEpoch(0));

void main() {
  testWidgets('idle state shows the search prompt', (tester) async {
    final cubits = TestCubits();
    addTearDown(cubits.close);

    await pumpApp(tester, _board(), cubits: cubits);
    await tester.pump();

    expect(find.textContaining('Sélectionnez une ligne'), findsOneWidget);
  });

  testWidgets('connecting state shows a spinner', (tester) async {
    final harness = StopUpdateHarness();
    final cubits = TestCubits(stopUpdate: harness.cubit);
    addTearDown(cubits.close);

    harness.connecting();
    await pumpApp(tester, _board(), cubits: cubits);
    await tester.pump();

    expect(find.byType(CircularProgressIndicator), findsOneWidget);
    harness.cubit.stop();
  });

  testWidgets('error state shows the message', (tester) async {
    final harness = StopUpdateHarness();
    final cubits = TestCubits(stopUpdate: harness.cubit);
    addTearDown(cubits.close);

    harness.error();
    await pumpApp(tester, _board(), cubits: cubits);
    await tester.pump();
    await tester.pump();

    expect(find.textContaining('Erreur'), findsOneWidget);
    harness.cubit.stop();
  });

  testWidgets('live but empty shows the no-departures message', (tester) async {
    final harness = StopUpdateHarness();
    final cubits = TestCubits(stopUpdate: harness.cubit);
    addTearDown(cubits.close);

    harness.live(const []);
    await pumpApp(tester, _board(), cubits: cubits);
    await tester.pump();
    await tester.pump();

    expect(find.text('Aucun départ planifié'), findsOneWidget);
    harness.cubit.stop();
  });

  testWidgets('live with many departures clamps to five rows', (tester) async {
    final harness = StopUpdateHarness();
    final cubits = TestCubits(stopUpdate: harness.cubit);
    addTearDown(cubits.close);

    harness.live(List.generate(7, (i) => sampleStopUpdate(tripId: 't$i')));
    await pumpApp(tester, _board(), cubits: cubits);
    await tester.pump();
    await tester.pump();

    expect(find.byType(DepartureRow), findsNWidgets(5));
    expect(find.byType(Divider), findsNWidgets(4));
    harness.cubit.stop();
  });
}
