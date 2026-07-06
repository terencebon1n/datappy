import 'package:flutter_test/flutter_test.dart';

import 'package:frontend/application/favorites/cubit.dart';
import 'package:frontend/domain/city.dart';
import 'package:frontend/domain/conveyance.dart';
import 'package:frontend/domain/direction.dart';
import 'package:frontend/domain/repositories/i_favorites_store.dart';
import 'package:frontend/domain/saved_selection.dart';

SavedSelection _fav(String id) => SavedSelection(
      city: City(name: 'Lyon'),
      conveyance: Conveyance(
        id: id,
        shortName: id,
        longName: id,
        colorValue: 0,
        typeId: 0,
        typeName: 'Tram',
      ),
      sourceStop: 'src-$id',
      destStop: 'dst-$id',
      direction: Direction(
        directionId: 0,
        stopIdOrigin: 'o',
        stopIdDestination: 'd',
      ),
    );

class _FakeFavoritesStore implements IFavoritesStore {
  List<SavedSelection> saved;

  _FakeFavoritesStore(this.saved);

  @override
  Future<List<SavedSelection>> load() async => saved;

  @override
  Future<void> save(List<SavedSelection> favorites) async {
    saved = favorites;
  }
}

Future<FavoritesCubit> _seeded(List<SavedSelection> initial) async {
  final cubit = FavoritesCubit(store: _FakeFavoritesStore(List.of(initial)));
  await Future<void>.delayed(Duration.zero); // let the async _init load finish
  return cubit;
}

void main() {
  final a = _fav('A');
  final b = _fav('B');
  final c = _fav('C');

  test('reorder moves an item down (ReorderableListView index convention)', () async {
    final cubit = await _seeded([a, b, c]);

    cubit.reorder(0, 3); // drag A past the end of the list

    expect(cubit.state, [b, c, a]);
    await cubit.close();
  });

  test('reorder moves an item up', () async {
    final cubit = await _seeded([a, b, c]);

    cubit.reorder(2, 0); // drag C to the front

    expect(cubit.state, [c, a, b]);
    await cubit.close();
  });

  test('reorder persists the new order to the store', () async {
    final store = _FakeFavoritesStore([a, b, c]);
    final cubit = FavoritesCubit(store: store);
    await Future<void>.delayed(Duration.zero);

    cubit.reorder(0, 3);

    expect(store.saved, [b, c, a]);
    await cubit.close();
  });

  test('reorder onto the same slot is a no-op', () async {
    final cubit = await _seeded([a, b]);

    cubit.reorder(0, 1); // newIndex collapses back to 0

    expect(cubit.state, [a, b]);
    await cubit.close();
  });
}
