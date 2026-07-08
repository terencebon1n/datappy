import 'dart:convert';

import 'package:flutter_test/flutter_test.dart';
import 'package:shared_preferences/shared_preferences.dart';

import 'package:frontend/infrastructure/local/favorites_store.dart';

import '../helpers/fakes.dart';

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  test('returns an empty list when nothing is stored', () async {
    SharedPreferences.setMockInitialValues({});
    final store = await SharedPrefsFavoritesStore.create();
    expect(await store.load(), isEmpty);
  });

  test('saves then loads favorites', () async {
    SharedPreferences.setMockInitialValues({});
    final store = await SharedPrefsFavoritesStore.create();
    final favorites = [sampleSelection(id: 'A'), sampleSelection(id: 'B')];

    await store.save(favorites);
    final restored = await store.load();

    expect(restored.map((f) => f.conveyance.id), ['A', 'B']);
  });

  test('returns an empty list for a corrupt blob', () async {
    SharedPreferences.setMockInitialValues({'favorites': 'not json {'});
    final store = await SharedPrefsFavoritesStore.create();
    expect(await store.load(), isEmpty);
  });

  test('skips corrupt entries but keeps the valid ones', () async {
    final raw = jsonEncode([
      {'garbage': true},
      sampleSelection(id: 'OK').toJson(),
    ]);
    SharedPreferences.setMockInitialValues({'favorites': raw});
    final store = await SharedPrefsFavoritesStore.create();

    final restored = await store.load();

    expect(restored, hasLength(1));
    expect(restored.single.conveyance.id, 'OK');
  });
}
