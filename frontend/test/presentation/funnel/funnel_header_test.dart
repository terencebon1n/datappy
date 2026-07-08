import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

import 'package:frontend/application/route_selection/state.dart' show FunnelStep;
import 'package:frontend/presentation/funnel/funnel_colors.dart';
import 'package:frontend/presentation/funnel/funnel_header.dart';

Future<void> _pump(
  WidgetTester tester, {
  bool leadingIsClose = false,
  FunnelStep? stepperFor,
  Widget? bottom,
  VoidCallback? onLeading,
}) {
  FunnelColors.apply(false);
  return tester.pumpWidget(
    MaterialApp(
      home: Scaffold(
        body: FunnelHeader(
          overline: 'Lyon',
          title: 'Quelle ligne ?',
          leadingIsClose: leadingIsClose,
          stepperFor: stepperFor,
          bottom: bottom,
          onLeading: onLeading ?? () {},
        ),
      ),
    ),
  );
}

void main() {
  testWidgets('close variant shows the close icon and fires onLeading', (tester) async {
    var tapped = false;
    await _pump(tester, leadingIsClose: true, onLeading: () => tapped = true);

    expect(find.byIcon(Icons.close), findsOneWidget);
    expect(find.text('QUELLE LIGNE ?'.toUpperCase()), findsNothing);
    expect(find.text('Quelle ligne ?'), findsOneWidget);

    await tester.tap(find.byIcon(Icons.close));
    expect(tapped, isTrue);
  });

  testWidgets('back variant shows the arrow icon', (tester) async {
    await _pump(tester, leadingIsClose: false);
    expect(find.byIcon(Icons.arrow_back), findsOneWidget);
  });

  testWidgets('stepper renders every step and an optional bottom widget',
      (tester) async {
    for (final step in FunnelStep.values) {
      await _pump(
        tester,
        stepperFor: step,
        bottom: const Text('bottom-slot'),
      );
      expect(find.text('Ligne'), findsOneWidget);
      expect(find.text('Départ'), findsOneWidget);
      expect(find.text('Arrivée'), findsOneWidget);
      expect(find.text('bottom-slot'), findsOneWidget);
    }
  });

  testWidgets('later steps mark earlier dots as done', (tester) async {
    await _pump(tester, stepperFor: FunnelStep.dest);
    expect(find.byIcon(Icons.check), findsWidgets);
  });
}
