import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:frontend/domain/conveyance.dart';
import 'package:frontend/domain/route_type.dart';
import 'package:frontend/domain/repositories/i_conveyance.dart';
import 'package:frontend/domain/repositories/i_direction.dart';
import 'package:frontend/domain/repositories/i_route_type.dart';
import 'package:frontend/domain/repositories/i_stop_name.dart';
import 'package:frontend/domain/path.dart';
import 'state.dart';


class RouteSelectionCubit extends Cubit<RouteSelectionState> {
  final IRouteTypeRepository _routeTypeRepo;
  final IConveyanceRepository _conveyanceRepo;
  final IStopNameRepository _stopRepo;
  final IDirectionRepository _directionRepo;

  RouteSelectionCubit({
    required IRouteTypeRepository routeTypeRepo,
    required IConveyanceRepository conveyanceRepo,
    required IStopNameRepository stopRepo,
    required IDirectionRepository directionRepo,
  })  : _routeTypeRepo = routeTypeRepo,
        _conveyanceRepo = conveyanceRepo,
        _stopRepo = stopRepo,
        _directionRepo = directionRepo,
        super(const RouteSelectionState()) {
    _loadRouteTypes();
  }

  Future<void> _loadRouteTypes() async {
    final routeTypes = await _routeTypeRepo.resolveRouteTypes();
    emit(state.copyWith(
      status: RouteSelectionStatus.ready,
      routeTypes: routeTypes,
    ));
  }

  Future<void> selectRouteType(RouteType type) async {
    emit(state.copyWith(
      selectedType: type,
      selectedConveyance: null,
      conveyances: [],
      stops: [],
      sourceStop: null,
      destStop: null,
      direction: null,
    ));
    final conveyances = await _conveyanceRepo.resolveConveyances(type);
    emit(state.copyWith(conveyances: conveyances));
  }

  Future<void> selectConveyance(Conveyance conveyance) async {
    emit(state.copyWith(
      selectedConveyance: conveyance,
      stops: [],
      sourceStop: null,
      destStop: null,
      direction: null,
    ));
    final stops = await _stopRepo.resolveStopNames(conveyance.id);
    emit(state.copyWith(stops: stops));
  }

  void selectSourceStop(String stop) {
      emit(state.copyWith(sourceStop: stop));
      _checkAndResolveDirection();
  }

  void selectDestStop(String stop) {
      emit(state.copyWith(destStop: stop));
      _checkAndResolveDirection();
  }

  Future<void> _checkAndResolveDirection() async {
    if (state.selectedConveyance != null &&
        state.sourceStop != null &&
        state.destStop != null &&
        state.sourceStop != state.destStop) {
      
      try {
        final directionData = await _directionRepo.resolveDirection(
          Path(
            routeId: state.selectedConveyance!.id,
            stopNameOrigin: state.sourceStop!,
            stopNameDestination: state.destStop!,
          ),
        );
        emit(state.copyWith(direction: directionData));
      } catch (e) {
        // Handle lookup failure gracefully depending on your error architecture
        emit(state.copyWith(direction: null)); 
      }
    }
  }
}
