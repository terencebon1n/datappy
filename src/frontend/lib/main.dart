import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';

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


Future<void> main() async {
    WidgetsFlutterBinding.ensureInitialized();
    final selectionStore = await SharedPrefsSelectionStore.create();
    final themeStore = await SharedPrefsThemeStore.create();
    final initialThemeMode = themeStore.load() ?? ThemeMode.system;
    final favoritesStore = await SharedPrefsFavoritesStore.create();

    runApp(
        MultiBlocProvider(
            providers: [
                BlocProvider(create: (context) => RouteSelectionCubit(
                    cityRepo: CityRepository(
                        apiBase: DatappyConfig.apiBase
                    ),
                    conveyanceRepo: ConveyanceRepository(
                        apiBase: DatappyConfig.apiBase
                    ),
                    stopRepo: StopNameRepository(
                        apiBase: DatappyConfig.apiBase
                    ),
                    directionRepo: DirectionRepository(
                        apiBase: DatappyConfig.apiBase
                    ),
                    selectionStore: selectionStore
                )),
                BlocProvider(create: (context) => StopUpdateCubit(
                    stopUpdateRepo: StopUpdateRepository(
                        wsBase: DatappyConfig.wsBase
                    ),
                    selectionStore: selectionStore
                )),
                BlocProvider(create: (context) => ThemeCubit(
                    store: themeStore,
                    initial: initialThemeMode
                )),
                BlocProvider(create: (context) => FavoritesCubit(
                    store: favoritesStore
                ))
            ],
            child: BlocBuilder<ThemeCubit, ThemeMode>(
                builder: (context, mode) {
                    final isDark = resolveIsDark(mode);
                    TransitColors.apply(isDark);
                    FunnelColors.apply(isDark);

                    return MaterialApp(
                        debugShowCheckedModeBanner: false,
                        themeMode: mode,
                        theme: ThemeData(brightness: Brightness.light),
                        darkTheme: ThemeData(brightness: Brightness.dark),
                        home: const TransitDashboard(),
                    );
                },
            ),
        ),
    );
}
