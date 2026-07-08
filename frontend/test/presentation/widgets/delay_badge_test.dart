import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

import 'package:frontend/presentation/theme/colors.dart';
import 'package:frontend/presentation/widgets/delay_badge.dart';

Future<void> _pump(WidgetTester tester, int delay) {
  TransitColors.apply(false);
  return tester.pumpWidget(
    MaterialApp(home: Scaffold(body: DelayBadge(delaySeconds: delay))),
  );
}

void main() {
  testWidgets('zero delay reads as on time', (tester) async {
    await _pump(tester, 0);
    expect(find.text("À l'heure"), findsOneWidget);
    expect(find.text('+0 s'), findsOneWidget);
  });

  testWidgets('small delay reads as a light delay', (tester) async {
    await _pump(tester, 60);
    expect(find.text('Léger retard'), findsOneWidget);
    expect(find.text('+1m 0s'), findsOneWidget);
  });

  testWidgets('large delay reads as disrupted', (tester) async {
    await _pump(tester, 300);
    expect(find.text('Perturbé'), findsOneWidget);
    expect(find.text('+5m 0s'), findsOneWidget);
  });
}
