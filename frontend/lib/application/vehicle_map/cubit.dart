import 'dart:async';

import 'package:flutter_bloc/flutter_bloc.dart';

import 'package:frontend/domain/city.dart' show City;
import 'package:frontend/domain/conveyance.dart' show Conveyance;
import 'package:frontend/domain/transit_path.dart' show TransitPath;
import 'package:frontend/domain/direction.dart' show Direction;
import 'package:frontend/domain/repositories/i_conveyance.dart'
    show IConveyanceRepository;
import 'package:frontend/domain/repositories/i_route_geometry.dart'
    show IRouteGeometryRepository;
import 'package:frontend/domain/repositories/i_vehicle_position.dart'
    show IVehiclePositionRepository;
import 'state.dart';

final _mapIgnoresDirection = Direction(
    directionId: 0,
    stopIdOrigin: '',
    stopIdDestination: '',
);

class VehicleMapCubit extends Cubit<VehicleMapState> {
    final IVehiclePositionRepository _vehicleRepo;
    final IRouteGeometryRepository _geometryRepo;
    final IConveyanceRepository _conveyanceRepo;

    StreamSubscription? _sub;
    City? _city;

    VehicleMapCubit({
        required IVehiclePositionRepository vehicleRepo,
        required IRouteGeometryRepository geometryRepo,
        required IConveyanceRepository conveyanceRepo,
    })  : _vehicleRepo = vehicleRepo,
          _geometryRepo = geometryRepo,
          _conveyanceRepo = conveyanceRepo,
          super(const VehicleMapState());

    City? get city => _city;

    Future<void> open({City? city, Conveyance? fallbackLine}) async {
        if (city == null) return;

        if (_city?.name != city.name) {
            _city = city;
            emit(state.copyWith(lines: const []));
            await _loadLines(city);
        }

        if (state.line == null && fallbackLine != null) {
            await selectLine(fallbackLine);
        }
    }

    Future<void> _loadLines(City city) async {
        try {
            emit(state.copyWith(lines: await _conveyanceRepo.resolveConveyances(city)));
        } catch (_) {
            emit(state.copyWith(lines: const []));
        }
    }

    Future<void> selectLine(Conveyance line) async {
        final city = _city;
        if (city == null) return;

        if (state.line?.id == line.id && state.status != VehicleMapStatus.error) {
            return;
        }

        await _sub?.cancel();
        _sub = null;
        emit(VehicleMapState(
            status: VehicleMapStatus.loading,
            line: line,
            lines: state.lines,
        ));

        try {
            final geometry = await _geometryRepo.resolveRouteGeometry(line.id, city);
            emit(state.copyWith(
                status: VehicleMapStatus.live,
                geometry: geometry,
            ));
        } catch (_) {
            emit(VehicleMapState(
                status: VehicleMapStatus.error,
                line: line,
                lines: state.lines,
            ));
            return;
        }

        _subscribe(city, line);
    }

    void _subscribe(City city, Conveyance line) {
        final path = TransitPath(
            city: city.name.toLowerCase(),
            routeId: line.id,
            direction: _mapIgnoresDirection,
        );

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
        _city = null;
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
