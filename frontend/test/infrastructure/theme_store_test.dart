import 'package:flutter/material.dart' show ThemeMode;
import 'package:flutter_test/flutter_test.dart';
import 'package:shared_preferences/shared_preferences.dart';

import 'package:frontend/infrastructure/local/theme_store.dart';

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  Future<SharedPrefsThemeStore> storeWith(Map<String, Object> values) async {
    SharedPreferences.setMockInitialValues(values);
    return SharedPrefsThemeStore.create();
  }

  group('load', () {
    test('maps each stored string to a ThemeMode', () async {
      expect((await storeWith({'theme_mode': 'light'})).load(), ThemeMode.light);
      expect((await storeWith({'theme_mode': 'dark'})).load(), ThemeMode.dark);
      expect((await storeWith({'theme_mode': 'system'})).load(), ThemeMode.system);
    });

    test('returns null for missing or unknown values', () async {
      expect((await storeWith({})).load(), isNull);
      expect((await storeWith({'theme_mode': 'weird'})).load(), isNull);
    });
  });

  test('save round-trips every mode', () async {
    for (final mode in ThemeMode.values) {
      final store = await storeWith({});
      await store.save(mode);
      expect(store.load(), mode);
    }
  });
}
