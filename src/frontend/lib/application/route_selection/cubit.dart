import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:frontend/domain/city.dart';
import 'package:frontend/domain/conveyance.dart';
import 'package:frontend/domain/repositories/i_city.dart';
import 'package:frontend/domain/repositories/i_conveyance.dart';
import 'package:frontend/domain/repositories/i_direction.dart';
import 'package:frontend/domain/repositories/i_stop_name.dart';
import 'package:frontend/domain/repositories/i_selection_store.dart';
import 'package:frontend/domain/saved_selection.dart';
import 'package:frontend/domain/path.dart';
import 'state.dart';


class RouteSelectionCubit extends Cubit<RouteSelectionState> {
  final ICityRepository _cityRepo;
  final IConveyanceRepository _conveyanceRepo;
  final IStopNameRepository _stopRepo;
  final IDirectionRepository _directionRepo;
  final ISelectionStore _selectionStore;

  RouteSelectionCubit({
    required ICityRepository cityRepo,
    required IConveyanceRepository conveyanceRepo,
    required IStopNameRepository stopRepo,
    required IDirectionRepository directionRepo,
    required ISelectionStore selectionStore,
  })  : _cityRepo = cityRepo,
        _conveyanceRepo = conveyanceRepo,
        _stopRepo = stopRepo,
        _directionRepo = directionRepo,
        _selectionStore = selectionStore,
        super(const RouteSelectionState()) {
    _init();
  }

  Future<void> _init() async {
    final saved = await _selectionStore.load();
    final cities = await _cityRepo.resolveCities();
    if (saved == null) {
      emit(state.copyWith(cities: cities));
      return;
    }
    emit(state.copyWith(
      cities: cities,
      selectedCity: saved.city,
      selectedConveyance: saved.conveyance,
      sourceStop: saved.sourceStop,
      destStop: saved.destStop,
      direction: saved.direction,
    ));
  }

  Future<void> loadSelection(SavedSelection s) async {
    emit(state.copyWith(
      selectedCity: s.city,
      selectedConveyance: s.conveyance,
      sourceStop: s.sourceStop,
      destStop: s.destStop,
      direction: s.direction,
    ));
    await _selectionStore.save(s);
  }

  SavedSelection? _previousSelection;

  void reset() {
    emit(RouteSelectionState(
      status: state.status,
      cities: state.cities,
    ));
  }

  void beginSearch() {
    _previousSelection = state.canSubmit
        ? SavedSelection(
            city: state.selectedCity!,
            conveyance: state.selectedConveyance!,
            sourceStop: state.sourceStop!,
            destStop: state.destStop!,
            direction: state.direction!,
          )
        : null;
    reset();
  }

  void cancelSearch() {
    final prev = _previousSelection;
    emit(RouteSelectionState(
      status: state.status,
      cities: state.cities,
      selectedCity: prev?.city,
      selectedConveyance: prev?.conveyance,
      sourceStop: prev?.sourceStop,
      destStop: prev?.destStop,
      direction: prev?.direction,
    ));
  }

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
    emit(_afterCity(city));
    final headers = {'City': city.name.toLowerCase()};
    _conveyanceRepo.headers = headers;
    _stopRepo.headers = headers;
    _directionRepo.headers = headers;
    final conveyances = await _conveyanceRepo.resolveConveyances();
    emit(state.copyWith(conveyances: conveyances));
  }

  Future<void> selectConveyance(Conveyance conveyance) async {
    emit(_afterConveyance(conveyance));
    final stops = await _stopRepo.resolveStopNames(conveyance.id);
    emit(state.copyWith(stops: stops));
  }

  void selectSourceStop(String stop) => emit(_afterSource(stop));

  void selectDestStop(String stop) {
    emit(_afterSource(state.sourceStop!, destStop: stop));
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
        await _selectionStore.save(SavedSelection(
          city: state.selectedCity!,
          conveyance: state.selectedConveyance!,
          sourceStop: state.sourceStop!,
          destStop: state.destStop!,
          direction: directionData,
        ));
      } catch (e) {
        emit(_afterSource(state.sourceStop!));
      }
    }
  }


  RouteSelectionState _afterCity(City city) => RouteSelectionState(
        status: state.status,
        step: FunnelStep.line,
        cities: state.cities,
        selectedCity: city,
      );

  RouteSelectionState _afterConveyance(Conveyance conveyance) =>
      RouteSelectionState(
        status: state.status,
        step: FunnelStep.source,
        cities: state.cities,
        conveyances: state.conveyances,
        selectedCity: state.selectedCity,
        selectedConveyance: conveyance,
      );

  RouteSelectionState _afterSource(String sourceStop, {String? destStop}) =>
      RouteSelectionState(
        status: state.status,
        step: FunnelStep.dest,
        cities: state.cities,
        conveyances: state.conveyances,
        stops: state.stops,
        selectedCity: state.selectedCity,
        selectedConveyance: state.selectedConveyance,
        sourceStop: sourceStop,
        destStop: destStop,
      );
}
