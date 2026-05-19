import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';

import 'package:frontend/infrastructure/backend/repositories/conveyance.dart' show ConveyanceRepository;
import 'package:frontend/infrastructure/backend/repositories/direction.dart' show DirectionRepository;
import 'package:frontend/infrastructure/backend/repositories/route_type.dart' show RouteTypeRepository;
import 'package:frontend/infrastructure/backend/repositories/stop_name.dart' show StopNameRepository;
import 'package:frontend/infrastructure/backend/repositories/stop_update.dart' show StopUpdateRepository;

import 'package:frontend/application/stop_update/cubit.dart' show StopUpdateCubit;
import 'package:frontend/application/route_selection/cubit.dart' show RouteSelectionCubit;
import 'package:frontend/config/datappy_config.dart' show DatappyConfig;

import 'package:frontend/presentation/transit_dashboard.dart' show TransitDashboard;


void main() {
    runApp(
        MultiBlocProvider(
            providers: [
                BlocProvider(create: (context) => RouteSelectionCubit(
                    routeTypeRepo: RouteTypeRepository(
                        apiBase: DatappyConfig.apiBase,
                        headers: {'City': 'montpellier'}
                    ),
                    conveyanceRepo: ConveyanceRepository(
                        apiBase: DatappyConfig.apiBase,
                        headers: {'City': 'montpellier'}
                    ),
                    stopRepo: StopNameRepository(
                        apiBase: DatappyConfig.apiBase,
                        headers: {'City': 'montpellier'}
                    ),
                    directionRepo: DirectionRepository(
                        apiBase: DatappyConfig.apiBase,
                        headers: {'City': 'montpellier'}
                    )
                )),
                BlocProvider(create: (context) => StopUpdateCubit(
                    stopUpdateRepo: StopUpdateRepository(
                        wsBase: DatappyConfig.wsBase
                    )
                ))
            ],
        child: const MaterialApp(
            debugShowCheckedModeBanner: false,
            home: TransitDashboard(),
          ),
        ),
    );
}
