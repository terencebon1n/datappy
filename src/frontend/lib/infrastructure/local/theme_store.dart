import 'package:flutter/material.dart' show ThemeMode;
import 'package:shared_preferences/shared_preferences.dart' show SharedPreferences;

import 'package:frontend/domain/repositories/i_theme_store.dart' show IThemeStore;


class SharedPrefsThemeStore implements IThemeStore {
    static const String _key = 'theme_mode';

    final SharedPreferences _prefs;

    SharedPrefsThemeStore._(this._prefs);

    static Future<SharedPrefsThemeStore> create() async =>
        SharedPrefsThemeStore._(await SharedPreferences.getInstance());

    @override
    ThemeMode? load() => switch (_prefs.getString(_key)) {
        'light'  => ThemeMode.light,
        'dark'   => ThemeMode.dark,
        'system' => ThemeMode.system,
        _        => null,
    };

    @override
    Future<void> save(ThemeMode mode) => _prefs.setString(_key, switch (mode) {
        ThemeMode.light  => 'light',
        ThemeMode.dark   => 'dark',
        ThemeMode.system => 'system',
    });
}
