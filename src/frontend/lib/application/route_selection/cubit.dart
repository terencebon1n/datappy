import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:frontend/domain/city.dart';
import 'package:frontend/domain/conveyance.dart';
import 'package:frontend/domain/repositories/i_city.dart';
import 'package:frontend/domain/repositories/i_conveyance.dart';
import 'package:frontend/domain/repositories/i_direction.dart';
import 'package:frontend/domain/repositories/i_stop_name.dart';
import 'package:frontend/domain/path.dart';
import 'state.dart';


class RouteSelectionCubit extends Cubit<RouteSelectionState> {
  final ICityRepository _cityRepo;
  final IConveyanceRepository _conveyanceRepo;
  final IStopNameRepository _stopRepo;
  final IDirectionRepository _directionRepo;

  RouteSelectionCubit({
    required ICityRepository cityRepo,
    required IConveyanceRepository conveyanceRepo,
    required IStopNameRepository stopRepo,
    required IDirectionRepository directionRepo,
  })  : _cityRepo = cityRepo,
        _conveyanceRepo = conveyanceRepo,
        _stopRepo = stopRepo,
        _directionRepo = directionRepo,
        super(const RouteSelectionState()) {
    _loadCity();
  }

  Future<void> _loadCity() async {
      final cities = await _cityRepo.resolveCities();
      emit(state.copyWith(cities: cities));
  }

  /// Restart a fresh search at the city step, keeping the loaded city list.
  void reset() {
    emit(RouteSelectionState(
      status: state.status,
      cities: state.cities,
    ));
  }

  /// Go back one step, preserving already-loaded data.
  /// Returns false when already at the first step (caller should pop the route).
  bool back() {
    final prev = switch (state.step) {
      FunnelStep.city => null,
      FunnelStep.line => FunnelStep.city,
      FunnelStep.source => FunnelStep.line,
      FunnelStep.dest => FunnelStep.source,
    };
    if (prev == null) return false;
    emit(state.copyWith(step: prev));
    return true;
  }

  Future<void> selectCity(City city) async {
    emit(RouteSelectionState(
      status: state.status,
      step: FunnelStep.line,
      cities: state.cities,
      selectedCity: city,
    ));
    final headers = {'City': city.name.toLowerCase()};
    _conveyanceRepo.headers = headers;
    _stopRepo.headers = headers;
    _directionRepo.headers = headers;
    final conveyances = await _conveyanceRepo.resolveConveyances();
    emit(state.copyWith(conveyances: conveyances));
  }

  Future<void> selectConveyance(Conveyance conveyance) async {
    emit(RouteSelectionState(
      status: state.status,
      step: FunnelStep.source,
      cities: state.cities,
      conveyances: state.conveyances,
      selectedCity: state.selectedCity,
      selectedConveyance: conveyance,
    ));
    final stops = await _stopRepo.resolveStopNames(conveyance.id);
    emit(state.copyWith(stops: stops));
  }

  void selectSourceStop(String stop) {
    emit(RouteSelectionState(
      status: state.status,
      step: FunnelStep.dest,
      cities: state.cities,
      conveyances: state.conveyances,
      stops: state.stops,
      selectedCity: state.selectedCity,
      selectedConveyance: state.selectedConveyance,
      sourceStop: stop,
    ));
  }

  void selectDestStop(String stop) {
    emit(RouteSelectionState(
      status: state.status,
      step: FunnelStep.dest,
      cities: state.cities,
      conveyances: state.conveyances,
      stops: state.stops,
      selectedCity: state.selectedCity,
      selectedConveyance: state.selectedConveyance,
      sourceStop: state.sourceStop,
      destStop: stop,
    ));
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
        // Resolution failed: clear the destination so the "resolving" overlay
        // disappears and the user can pick another arrival stop.
        emit(RouteSelectionState(
          status: state.status,
          step: FunnelStep.dest,
          cities: state.cities,
          conveyances: state.conveyances,
          stops: state.stops,
          selectedCity: state.selectedCity,
          selectedConveyance: state.selectedConveyance,
          sourceStop: state.sourceStop,
        ));
      }
    }
  }
}
