import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

import 'package:frontend/presentation/theme/colors.dart';
import 'package:frontend/presentation/widgets/live_pill.dart';

void main() {
  testWidgets('live pill pulses and shows the realtime label', (tester) async {
    TransitColors.apply(false);
    await tester.pumpWidget(
      const MaterialApp(home: Scaffold(body: Center(child: LivePill(isLive: true)))),
    );

    expect(find.text('TEMPS RÉEL'), findsOneWidget);
    await tester.pump(const Duration(milliseconds: 400));
    await tester.pump(const Duration(milliseconds: 400));

    await tester.pumpWidget(const SizedBox());
  });

  testWidgets('waiting pill shows the idle label', (tester) async {
    TransitColors.apply(false);
    await tester.pumpWidget(
      const MaterialApp(home: Scaffold(body: Center(child: LivePill(isLive: false)))),
    );

    expect(find.text('EN ATTENTE'), findsOneWidget);
    await tester.pumpWidget(const SizedBox());
  });
}
