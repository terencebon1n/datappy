import 'package:flutter/material.dart' show ThemeMode, Brightness, WidgetsBinding;
import 'package:flutter_bloc/flutter_bloc.dart';

import 'package:frontend/domain/repositories/i_theme_store.dart';


bool resolveIsDark(ThemeMode mode) => switch (mode) {
    ThemeMode.dark   => true,
    ThemeMode.light  => false,
    ThemeMode.system =>
        WidgetsBinding.instance.platformDispatcher.platformBrightness ==
            Brightness.dark,
};


class ThemeCubit extends Cubit<ThemeMode> {
    final IThemeStore _store;

    ThemeCubit({required IThemeStore store, required ThemeMode initial})
        : _store = store,
          super(initial);

    void toggle() {
        final next = resolveIsDark(state) ? ThemeMode.light : ThemeMode.dark;
        emit(next);
        _store.save(next);
    }
}
