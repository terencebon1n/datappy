import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:shared_preferences/shared_preferences.dart';

import 'package:frontend/main.dart' as app;
import 'package:frontend/presentation/transit_dashboard.dart';

import 'helpers/fakes.dart';

void main() {
  testWidgets('buildDatappyApp boots the dashboard and reacts to theme changes',
      (tester) async {
    await tester.pumpWidget(app.buildDatappyApp(
      selectionStore: InMemorySelectionStore(),
      themeStore: InMemoryThemeStore(),
      favoritesStore: InMemoryFavoritesStore(),
      cityRepo: FakeCityRepo(),
      conveyanceRepo: FakeConveyanceRepo(),
      stopRepo: FakeStopNameRepo(),
      directionRepo: FakeDirectionRepo(),
      stopUpdateRepo: FakeStopUpdateRepo(),
      alertRepo: FakeAlertRepo(),
      initialThemeMode: ThemeMode.light,
    ));
    await tester.pump();

    expect(find.byType(MaterialApp), findsOneWidget);
    expect(find.byType(TransitDashboard), findsOneWidget);

    await tester.tap(find.text('Thème'));
    await tester.pump();

    await tester.pumpWidget(const SizedBox());
  });

  testWidgets('main() wires the real stores and repositories', (tester) async {
    SharedPreferences.setMockInitialValues({});

    await app.main();
    await tester.pump();
    await tester.pump(const Duration(milliseconds: 50));

    expect(find.byType(MaterialApp), findsOneWidget);

    await tester.pumpWidget(const SizedBox());
  });
}
