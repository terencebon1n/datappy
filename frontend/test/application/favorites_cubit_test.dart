import 'package:flutter_test/flutter_test.dart';

import 'package:frontend/application/favorites/cubit.dart';

import '../helpers/fakes.dart';

Future<FavoritesCubit> seeded(List favorites) async {
  final cubit = FavoritesCubit(
    store: InMemoryFavoritesStore(List.of(favorites.cast())),
  );
  await Future<void>.delayed(Duration.zero);
  return cubit;
}

void main() {
  final a = sampleSelection(id: 'A');
  final b = sampleSelection(id: 'B');

  test('_init seeds the state from the store', () async {
    final cubit = await seeded([a, b]);
    expect(cubit.state, [a, b]);
    await cubit.close();
  });

  test('add appends and ignores duplicates', () async {
    final store = InMemoryFavoritesStore();
    final cubit = FavoritesCubit(store: store);
    await Future<void>.delayed(Duration.zero);

    cubit.add(a);
    expect(cubit.state, [a]);
    expect(store.saved, [a]);

    cubit.add(a);
    expect(cubit.state, [a]);
    await cubit.close();
  });

  test('remove drops a present favorite and ignores absent ones', () async {
    final cubit = await seeded([a, b]);

    cubit.remove(b);
    expect(cubit.state, [a]);

    cubit.remove(b);
    expect(cubit.state, [a]);
    await cubit.close();
  });

  test('isFavorite reflects membership', () async {
    final cubit = await seeded([a]);
    expect(cubit.isFavorite(a), isTrue);
    expect(cubit.isFavorite(b), isFalse);
    await cubit.close();
  });

  test('toggle adds then removes, returning the new state', () async {
    final cubit = await seeded([]);

    expect(cubit.toggle(a), isTrue);
    expect(cubit.state, [a]);

    expect(cubit.toggle(a), isFalse);
    expect(cubit.state, isEmpty);
    await cubit.close();
  });

  test('reorder takes already-adjusted indices, so 0 -> 1 swaps', () async {
    final cubit = await seeded([a, b]);
    cubit.reorder(0, 1);
    expect(cubit.state, [b, a]);
    await cubit.close();
  });
}
