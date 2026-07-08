import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';

import 'package:frontend/domain/repositories/i_city.dart' show ICityRepository;
import 'package:frontend/domain/repositories/i_conveyance.dart' show IConveyanceRepository;
import 'package:frontend/domain/repositories/i_direction.dart' show IDirectionRepository;
import 'package:frontend/domain/repositories/i_stop_name.dart' show IStopNameRepository;
import 'package:frontend/domain/repositories/i_stop_update.dart' show IStopUpdateRepository;
import 'package:frontend/domain/repositories/i_selection_store.dart' show ISelectionStore;
import 'package:frontend/domain/repositories/i_theme_store.dart' show IThemeStore;
import 'package:frontend/domain/repositories/i_favorites_store.dart' show IFavoritesStore;

import 'package:frontend/infrastructure/backend/repositories/city.dart' show CityRepository;
import 'package:frontend/infrastructure/backend/repositories/conveyance.dart' show ConveyanceRepository;
import 'package:frontend/infrastructure/backend/repositories/direction.dart' show DirectionRepository;
import 'package:frontend/infrastructure/backend/repositories/stop_name.dart' show StopNameRepository;
import 'package:frontend/infrastructure/backend/repositories/stop_update.dart' show StopUpdateRepository;
import 'package:frontend/infrastructure/local/selection_store.dart' show SharedPrefsSelectionStore;
import 'package:frontend/infrastructure/local/theme_store.dart' show SharedPrefsThemeStore;
import 'package:frontend/infrastructure/local/favorites_store.dart' show SharedPrefsFavoritesStore;

import 'package:frontend/application/stop_update/cubit.dart' show StopUpdateCubit;
import 'package:frontend/application/route_selection/cubit.dart' show RouteSelectionCubit;
import 'package:frontend/application/favorites/cubit.dart' show FavoritesCubit;
import 'package:frontend/application/theme/cubit.dart' show ThemeCubit, resolveIsDark;
import 'package:frontend/config/datappy_config.dart' show DatappyConfig;

import 'package:frontend/presentation/theme/colors.dart' show TransitColors;
import 'package:frontend/presentation/funnel/funnel_colors.dart' show FunnelColors;
import 'package:frontend/presentation/transit_dashboard.dart' show TransitDashboard;

Widget buildDatappyApp({
    required ISelectionStore selectionStore,
    required IThemeStore themeStore,
    required IFavoritesStore favoritesStore,
    required ICityRepository cityRepo,
    required IConveyanceRepository conveyanceRepo,
    required IStopNameRepository stopRepo,
    required IDirectionRepository directionRepo,
    required IStopUpdateRepository stopUpdateRepo,
    required ThemeMode initialThemeMode,
}) {
    return MultiBlocProvider(
        providers: [
            BlocProvider(create: (context) => RouteSelectionCubit(
                cityRepo: cityRepo,
                conveyanceRepo: conveyanceRepo,
                stopRepo: stopRepo,
                directionRepo: directionRepo,
                selectionStore: selectionStore,
            )),
            BlocProvider(create: (context) => StopUpdateCubit(
                stopUpdateRepo: stopUpdateRepo,
                selectionStore: selectionStore,
            )),
            BlocProvider(create: (context) => ThemeCubit(
                store: themeStore,
                initial: initialThemeMode,
            )),
            BlocProvider(create: (context) => FavoritesCubit(
                store: favoritesStore,
            )),
        ],
        child: BlocBuilder<ThemeCubit, ThemeMode>(
            builder: (context, mode) {
                final isDark = resolveIsDark(mode);
                TransitColors.apply(isDark);
                FunnelColors.apply(isDark);

                return MaterialApp(
                    title: 'Datappy',
                    debugShowCheckedModeBanner: false,
                    themeMode: mode,
                    theme: ThemeData(brightness: Brightness.light),
                    darkTheme: ThemeData(brightness: Brightness.dark),
                    home: const TransitDashboard(),
                );
            },
        ),
    );
}

Future<void> main() async {
    WidgetsFlutterBinding.ensureInitialized();
    final selectionStore = await SharedPrefsSelectionStore.create();
    final themeStore = await SharedPrefsThemeStore.create();
    final favoritesStore = await SharedPrefsFavoritesStore.create();

    runApp(buildDatappyApp(
        selectionStore: selectionStore,
        themeStore: themeStore,
        favoritesStore: favoritesStore,
        cityRepo: CityRepository(apiBase: DatappyConfig.apiBase),
        conveyanceRepo: ConveyanceRepository(apiBase: DatappyConfig.apiBase),
        stopRepo: StopNameRepository(apiBase: DatappyConfig.apiBase),
        directionRepo: DirectionRepository(apiBase: DatappyConfig.apiBase),
        stopUpdateRepo: StopUpdateRepository(wsBase: DatappyConfig.wsBase),
        initialThemeMode: themeStore.load() ?? ThemeMode.system,
    ));
}
