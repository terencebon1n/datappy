import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

import 'package:frontend/application/favorites/cubit.dart';
import 'package:frontend/domain/saved_selection.dart';
import 'package:frontend/presentation/favorites/favorites_page.dart';

import '../helpers/fakes.dart';
import '../helpers/pump.dart';

SavedSelection _fav(String source, String dest) => SavedSelection(
      city: sampleCity(),
      conveyance: sampleConveyance(id: '$source$dest'),
      sourceStop: source,
      destStop: dest,
      direction: sampleDirection(),
    );

Future<FavoritesCubit> _seeded(WidgetTester tester, List<SavedSelection> initial) =>
    setUpAsync(tester, () async {
      final cubit = FavoritesCubit(store: InMemoryFavoritesStore(List.of(initial)));
      await Future<void>.delayed(Duration.zero);
      return cubit;
    });

void main() {
  testWidgets('empty state invites saving a favourite', (tester) async {
    final favorites = await _seeded(tester, []);
    final cubits = TestCubits(favorites: favorites);
    addTearDown(cubits.close);

    await pumpApp(tester, Scaffold(body: FavoritesPage(onSelect: (_) {})), cubits: cubits);
    await tester.pump();

    expect(find.text('Aucun favori'), findsOneWidget);
    expect(find.byIcon(Icons.favorite_border_rounded), findsOneWidget);
  });

  testWidgets('tapping a tile selects that favourite', (tester) async {
    SavedSelection? selected;
    final favorites = await _seeded(tester, [_fav('Alpha', 'Beta'), _fav('Gamma', 'Delta')]);
    final cubits = TestCubits(favorites: favorites);
    addTearDown(cubits.close);

    await pumpApp(
      tester,
      Scaffold(body: FavoritesPage(onSelect: (f) => selected = f)),
      cubits: cubits,
    );
    await tester.pump();

    expect(find.text('Alpha → Beta'), findsOneWidget);
    expect(find.text('LYON'), findsNWidgets(2));

    await tester.tap(find.text('Alpha → Beta'));
    expect(selected, _fav('Alpha', 'Beta'));
  });

  testWidgets('delete button removes the favourite', (tester) async {
    final favorites = await _seeded(tester, [_fav('Alpha', 'Beta'), _fav('Gamma', 'Delta')]);
    final cubits = TestCubits(favorites: favorites);
    addTearDown(cubits.close);

    await pumpApp(tester, Scaffold(body: FavoritesPage(onSelect: (_) {})), cubits: cubits);
    await tester.pump();

    await tester.tap(find.byIcon(Icons.delete_outline_rounded).first);
    await tester.pump();

    expect(find.text('Alpha → Beta'), findsNothing);
    expect(favorites.state, hasLength(1));
  });

  testWidgets('swiping a tile dismisses it', (tester) async {
    final favorites = await _seeded(tester, [_fav('Alpha', 'Beta'), _fav('Gamma', 'Delta')]);
    final cubits = TestCubits(favorites: favorites);
    addTearDown(cubits.close);

    await pumpApp(tester, Scaffold(body: FavoritesPage(onSelect: (_) {})), cubits: cubits);
    await tester.pump();

    await tester.drag(find.text('Gamma → Delta'), const Offset(-500, 0));
    await tester.pumpAndSettle();

    expect(find.text('Gamma → Delta'), findsNothing);
    expect(favorites.state, hasLength(1));
  });

  testWidgets('onReorderItem rewires the list order', (tester) async {
    final favorites = await _seeded(tester, [_fav('Alpha', 'Beta'), _fav('Gamma', 'Delta')]);
    final cubits = TestCubits(favorites: favorites);
    addTearDown(cubits.close);

    await pumpApp(tester, Scaffold(body: FavoritesPage(onSelect: (_) {})), cubits: cubits);
    await tester.pump();

    final list = tester.widget<ReorderableListView>(find.byType(ReorderableListView));
    list.onReorderItem!(0, 1);
    await tester.pump();

    expect(favorites.state.first, _fav('Gamma', 'Delta'));
  });
}
