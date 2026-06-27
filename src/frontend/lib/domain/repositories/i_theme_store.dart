import 'package:flutter/material.dart' show ThemeMode;


/// Persists the user's theme choice across app restarts.
abstract class IThemeStore {
    /// The saved mode, or null when the user has never chosen one (first launch).
    ThemeMode? load();

    Future<void> save(ThemeMode mode);
}
