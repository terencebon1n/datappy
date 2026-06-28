import 'package:flutter/material.dart' show ThemeMode;


abstract class IThemeStore {
    ThemeMode? load();

    Future<void> save(ThemeMode mode);
}
