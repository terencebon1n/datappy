import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

import 'package:frontend/presentation/funnel/funnel_colors.dart';
import 'package:frontend/presentation/funnel/funnel_widgets.dart';

import '../../helpers/fakes.dart';

Future<void> _host(WidgetTester tester, Widget child) {
  FunnelColors.apply(false);
  return tester.pumpWidget(MaterialApp(home: Scaffold(body: child)));
}

void main() {
  group('routeExtendedName', () {
    test('includes the long name when present', () {
      expect(routeExtendedName(sampleConveyance(id: 'T1', longName: 'Perrache')),
          'T1 - Perrache');
    });

    test('falls back to the id when the long name is empty', () {
      expect(routeExtendedName(sampleConveyance(id: 'T1', longName: '')), 'T1');
    });
  });

  testWidgets('FunnelSectionLabel uppercases its text', (tester) async {
    await _host(tester, const FunnelSectionLabel('réseaux'));
    expect(find.text('RÉSEAUX'), findsOneWidget);
  });

  testWidgets('RouteBadge with a near-white colour uses the type palette',
      (tester) async {
    await _host(
      tester,
      RouteBadge(sampleConveyance(colorValue: 0xFFFFFFFF, shortName: 'WW')),
    );
    expect(find.text('WW'), findsOneWidget);
    expect(find.byType(Icon), findsOneWidget);
  });

  testWidgets('RouteBadge with an empty short name shows only the icon',
      (tester) async {
    await _host(
      tester,
      RouteBadge(sampleConveyance(colorValue: 0xFF0080C0, shortName: '')),
    );
    expect(find.byType(Icon), findsOneWidget);
    expect(find.byType(Text), findsNothing);
  });

  testWidgets('RouteListTile shows the name and reports taps', (tester) async {
    var tapped = false;
    await _host(
      tester,
      RouteListTile(
        conveyance: sampleConveyance(id: 'T1', longName: 'Debourg'),
        onTap: () => tapped = true,
      ),
    );
    expect(find.text('T1 - Debourg'), findsOneWidget);

    await tester.tap(find.text('T1 - Debourg'));
    expect(tapped, isTrue);
  });

  testWidgets('FunnelSelectionBar hides the origin row when null', (tester) async {
    await _host(tester, FunnelSelectionBar(line: sampleConveyance()));
    expect(find.textContaining('Départ ·'), findsNothing);
  });

  testWidgets('FunnelSelectionBar shows the origin when provided', (tester) async {
    await _host(
      tester,
      FunnelSelectionBar(line: sampleConveyance(), origin: 'Perrache'),
    );
    expect(find.text('Départ · Perrache'), findsOneWidget);
  });
}
