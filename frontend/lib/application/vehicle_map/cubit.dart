import 'dart:async';

import 'package:flutter_bloc/flutter_bloc.dart';

import 'package:frontend/domain/city.dart' show City;
import 'package:frontend/domain/transit_path.dart' show TransitPath;
import 'package:frontend/domain/repositories/i_route_geometry.dart'
    show IRouteGeometryRepository;
import 'package:frontend/domain/repositories/i_vehicle_position.dart'
    show IVehiclePositionRepository;
import 'state.dart';


class VehicleMapCubit extends Cubit<VehicleMapState> {
    final IVehiclePositionRepository _vehicleRepo;
    final IRouteGeometryRepository _geometryRepo;

    StreamSubscription? _sub;
    TransitPath? _current;

    VehicleMapCubit({
        required IVehiclePositionRepository vehicleRepo,
        required IRouteGeometryRepository geometryRepo,
    })  : _vehicleRepo = vehicleRepo,
          _geometryRepo = geometryRepo,
          super(const VehicleMapState());

    Future<void> watch(TransitPath path) async {
        if (_current?.routeId == path.routeId &&
            _current?.city == path.city &&
            state.status != VehicleMapStatus.error) {
            return;
        }

        _current = path;
        await _sub?.cancel();
        _sub = null;
        emit(const VehicleMapState(status: VehicleMapStatus.loading));

        try {
            final geometry = await _geometryRepo.resolveRouteGeometry(
                path.routeId,
                City(name: path.city),
            );
            emit(state.copyWith(
                status: VehicleMapStatus.live,
                geometry: geometry,
            ));
        } catch (_) {
            emit(const VehicleMapState(status: VehicleMapStatus.error));
            return;
        }

        _subscribe(path);
    }

    void _subscribe(TransitPath path) {
        try {
            _sub = _vehicleRepo.watchVehiclePositions(path).listen(
                (vehicles) => emit(state.copyWith(
                    status: VehicleMapStatus.live,
                    vehicles: vehicles,
                )),
                onError: (_) => emit(state.copyWith(status: VehicleMapStatus.error)),
                onDone: () => emit(state.copyWith(status: VehicleMapStatus.error)),
            );
        } catch (_) {
            emit(state.copyWith(status: VehicleMapStatus.error));
        }
    }

    Future<void> stop() async {
        _current = null;
        await _sub?.cancel();
        _sub = null;
        emit(const VehicleMapState());
    }

    @override
    Future<void> close() {
        _sub?.cancel();
        return super.close();
    }
}
