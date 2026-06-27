import 'package:flutter/material.dart' show ThemeMode, Brightness, WidgetsBinding;
import 'package:flutter_bloc/flutter_bloc.dart';

import 'package:frontend/domain/repositories/i_theme_store.dart';


/// Resolves a [ThemeMode] to a concrete brightness, reading the device setting
/// when the mode is [ThemeMode.system].
bool resolveIsDark(ThemeMode mode) => switch (mode) {
    ThemeMode.dark   => true,
    ThemeMode.light  => false,
    ThemeMode.system =>
        WidgetsBinding.instance.platformDispatcher.platformBrightness ==
            Brightness.dark,
};


/// Holds the active [ThemeMode] and persists changes. Starts from the saved
/// preference, or [ThemeMode.system] on first launch so the app follows the
/// device's light/dark setting.
class ThemeCubit extends Cubit<ThemeMode> {
    final IThemeStore _store;

    ThemeCubit({required IThemeStore store, required ThemeMode initial})
        : _store = store,
          super(initial);

    /// Flips between light and dark based on what is currently showing, then
    /// persists the explicit choice.
    void toggle() {
        final next = resolveIsDark(state) ? ThemeMode.light : ThemeMode.dark;
        emit(next);
        _store.save(next);
    }
}
