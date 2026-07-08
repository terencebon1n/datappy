import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

import 'package:frontend/application/theme/cubit.dart';

import '../helpers/fakes.dart';

void main() {
  final binding = TestWidgetsFlutterBinding.ensureInitialized();

  tearDown(() => binding.platformDispatcher.clearPlatformBrightnessTestValue());

  group('resolveIsDark', () {
    test('dark and light modes are explicit', () {
      expect(resolveIsDark(ThemeMode.dark), isTrue);
      expect(resolveIsDark(ThemeMode.light), isFalse);
    });

    test('system mode follows the platform brightness', () {
      binding.platformDispatcher.platformBrightnessTestValue = Brightness.dark;
      expect(resolveIsDark(ThemeMode.system), isTrue);
      binding.platformDispatcher.platformBrightnessTestValue = Brightness.light;
      expect(resolveIsDark(ThemeMode.system), isFalse);
    });
  });

  group('toggle', () {
    test('dark -> light and persists', () async {
      final store = InMemoryThemeStore();
      final cubit = ThemeCubit(store: store, initial: ThemeMode.dark);

      cubit.toggle();

      expect(cubit.state, ThemeMode.light);
      expect(store.mode, ThemeMode.light);
      await cubit.close();
    });

    test('light -> dark and persists', () async {
      final store = InMemoryThemeStore();
      final cubit = ThemeCubit(store: store, initial: ThemeMode.light);

      cubit.toggle();

      expect(cubit.state, ThemeMode.dark);
      expect(store.mode, ThemeMode.dark);
      await cubit.close();
    });
  });
}
