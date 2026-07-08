import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

import 'package:frontend/application/theme/cubit.dart';
import 'package:frontend/presentation/widgets/bottom_nav.dart';

import '../../helpers/fakes.dart';
import '../../helpers/pump.dart';

void main() {
  testWidgets('reports home and favorites taps', (tester) async {
    int? tapped;
    final cubits = TestCubits();
    addTearDown(cubits.close);

    await pumpApp(
      tester,
      BottomNav(index: 0, onTap: (i) => tapped = i),
      cubits: cubits,
    );

    await tester.tap(find.text('Accueil'));
    expect(tapped, 0);
    await tester.tap(find.text('Favoris'));
    expect(tapped, 1);
  });

  testWidgets('theme button reflects the mode and flips it on tap', (tester) async {
    final theme = ThemeCubit(store: InMemoryThemeStore(), initial: ThemeMode.dark);
    final cubits = TestCubits(theme: theme);
    addTearDown(cubits.close);

    await pumpApp(
      tester,
      BottomNav(index: 1, onTap: (_) {}),
      cubits: cubits,
    );

    expect(find.byIcon(Icons.light_mode_rounded), findsOneWidget);

    await tester.tap(find.text('Thème'));
    await tester.pump();

    expect(theme.state, ThemeMode.light);
    expect(find.byIcon(Icons.dark_mode_rounded), findsOneWidget);
  });
}
