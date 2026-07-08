import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:flutter_test/flutter_test.dart';

import 'package:frontend/application/route_selection/cubit.dart';
import 'package:frontend/application/stop_update/cubit.dart';
import 'package:frontend/application/theme/cubit.dart';
import 'package:frontend/application/favorites/cubit.dart';
import 'package:frontend/presentation/theme/colors.dart';
import 'package:frontend/presentation/funnel/funnel_colors.dart';

import 'fakes.dart';

Future<void> pumpFrames(
  WidgetTester tester, {
  int frames = 10,
  Duration step = const Duration(milliseconds: 100),
}) async {
  for (var i = 0; i < frames; i++) {
    await tester.pump(step);
  }
}

Future<T> setUpAsync<T extends Object>(
  WidgetTester tester,
  Future<T> Function() body,
) async =>
    (await tester.runAsync<T>(body))!;

class StopUpdateHarness {
  final FakeStopUpdateRepo repo = FakeStopUpdateRepo();
  late final StopUpdateCubit cubit = StopUpdateCubit(
    stopUpdateRepo: repo,
    selectionStore: InMemorySelectionStore(),
  );

  void connecting() => cubit.watchStopUpdates(sampleTransitPath());

  void error() {
    cubit.watchStopUpdates(sampleTransitPath());
    repo.controller.addError(Exception('lost'));
  }

  void live(List updates) {
    cubit.watchStopUpdates(sampleTransitPath());
    repo.controller.add(updates.cast());
  }
}

class TestCubits {
  TestCubits({
    RouteSelectionCubit? routeSelection,
    StopUpdateCubit? stopUpdate,
    ThemeCubit? theme,
    FavoritesCubit? favorites,
  })  : routeSelection = routeSelection ??
            RouteSelectionCubit(
              cityRepo: FakeCityRepo(),
              conveyanceRepo: FakeConveyanceRepo(),
              stopRepo: FakeStopNameRepo(),
              directionRepo: FakeDirectionRepo(),
              selectionStore: InMemorySelectionStore(),
            ),
        stopUpdate = stopUpdate ??
            StopUpdateCubit(
              stopUpdateRepo: FakeStopUpdateRepo(),
              selectionStore: InMemorySelectionStore(),
            ),
        theme = theme ??
            ThemeCubit(store: InMemoryThemeStore(), initial: ThemeMode.light),
        favorites =
            favorites ?? FavoritesCubit(store: InMemoryFavoritesStore());

  final RouteSelectionCubit routeSelection;
  final StopUpdateCubit stopUpdate;
  final ThemeCubit theme;
  final FavoritesCubit favorites;

  Future<void> close() async {
    await routeSelection.close();
    await stopUpdate.close();
    await theme.close();
    await favorites.close();
  }
}

Future<TestCubits> pumpApp(
  WidgetTester tester,
  Widget home, {
  TestCubits? cubits,
  ThemeData? theme,
}) async {
  TransitColors.apply(false);
  FunnelColors.apply(false);
  final c = cubits ?? TestCubits();
  await tester.pumpWidget(
    MultiBlocProvider(
      providers: [
        BlocProvider.value(value: c.routeSelection),
        BlocProvider.value(value: c.stopUpdate),
        BlocProvider.value(value: c.theme),
        BlocProvider.value(value: c.favorites),
      ],
      child: MaterialApp(theme: theme, home: home),
    ),
  );
  return c;
}
