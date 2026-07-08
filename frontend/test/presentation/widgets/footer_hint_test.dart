import 'package:flutter/widgets.dart';
import 'package:flutter_test/flutter_test.dart';

import 'package:frontend/presentation/widgets/footer_hint.dart';

import '../../helpers/pump.dart';

void main() {
  testWidgets('is hidden when the feed is not live', (tester) async {
    final cubits = TestCubits();
    addTearDown(cubits.close);

    await pumpApp(tester, FooterHint(key: UniqueKey()), cubits: cubits);
    await tester.pump();

    expect(find.textContaining('GTFS Realtime'), findsNothing);
  });

  testWidgets('shows the realtime hint when live', (tester) async {
    final harness = StopUpdateHarness();
    final cubits = TestCubits(stopUpdate: harness.cubit);
    addTearDown(cubits.close);

    harness.live(const []);
    await pumpApp(tester, const FooterHint(), cubits: cubits);
    await tester.pump();
    await tester.pump();

    expect(find.textContaining('GTFS Realtime'), findsOneWidget);
    harness.cubit.stop();
  });
}
