import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

import 'package:frontend/application/route_selection/cubit.dart';
import 'package:frontend/presentation/widgets/top_bar.dart';

import '../../helpers/fakes.dart';
import '../../helpers/pump.dart';

Future<RouteSelectionCubit> _selectedCubit() async {
  final cubit = RouteSelectionCubit(
    cityRepo: FakeCityRepo(),
    conveyanceRepo: FakeConveyanceRepo(),
    stopRepo: FakeStopNameRepo(),
    directionRepo: FakeDirectionRepo(),
    selectionStore: InMemorySelectionStore(),
  );
  await cubit.loadSelection(sampleSelection());
  return cubit;
}

void main() {
  testWidgets('empty selection: no stop and a disabled favourite button',
      (tester) async {
    final cubits = TestCubits();
    addTearDown(cubits.close);

    await pumpApp(
      tester,
      Scaffold(body: TopBar(onSearchTap: () {})),
      cubits: cubits,
    );
    await tester.pump();

    expect(find.text('Aucun arrêt'), findsOneWidget);
    expect(find.text('ARRÊT SÉLECTIONNÉ'), findsOneWidget);
    expect(find.byIcon(Icons.favorite_border_rounded), findsOneWidget);
  });

  testWidgets('search button fires its callback', (tester) async {
    var tapped = false;
    final cubits = TestCubits();
    addTearDown(cubits.close);

    await pumpApp(
      tester,
      Scaffold(body: TopBar(onSearchTap: () => tapped = true)),
      cubits: cubits,
    );
    await tester.tap(find.byIcon(Icons.search_rounded));
    expect(tapped, isTrue);
  });

  testWidgets('full selection: shows meta and toggles the favourite with a snackbar',
      (tester) async {
    final routeSelection = await _selectedCubit();
    final cubits = TestCubits(routeSelection: routeSelection);
    addTearDown(cubits.close);

    await pumpApp(
      tester,
      Scaffold(body: TopBar(onSearchTap: () {})),
      cubits: cubits,
    );
    await tester.pump();

    expect(find.text('Perrache'), findsOneWidget);
    expect(find.textContaining('TRAMWAY'), findsOneWidget);
    expect(find.byIcon(Icons.favorite_border_rounded), findsOneWidget);

    await tester.tap(find.byIcon(Icons.favorite_border_rounded));
    await tester.pump();
    expect(find.text('Ajouté aux favoris'), findsOneWidget);
    expect(find.byIcon(Icons.favorite_rounded), findsOneWidget);

    await tester.tap(find.byIcon(Icons.favorite_rounded));
    await tester.pump();
    expect(find.text('Retiré des favoris'), findsOneWidget);
  });
}
