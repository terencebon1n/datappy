import 'dart:async';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:frontend/domain/transit_path.dart' show TransitPath;
import 'package:frontend/domain/repositories/i_stop_update.dart' show IStopUpdateRepository;
import 'package:frontend/domain/repositories/i_selection_store.dart' show ISelectionStore;
import 'state.dart';


class StopUpdateCubit extends Cubit<StopUpdateState> {
  final IStopUpdateRepository _stopUpdateRepo;
  final ISelectionStore _selectionStore;
  StreamSubscription? _sub;

  StopUpdateCubit({
    required IStopUpdateRepository stopUpdateRepo,
    required ISelectionStore selectionStore,
  })  : _stopUpdateRepo = stopUpdateRepo,
        _selectionStore = selectionStore,
        super(const StopUpdateIdle()) {
    _restore();
  }

  /// If a previous selection was persisted, reconnect its live feed on launch.
  /// A failed reconnect falls back silently to idle (no error banner). The
  /// path is built the same way the funnel does it when a search completes.
  Future<void> _restore() async {
    final saved = await _selectionStore.load();
    if (saved == null) return;
    await watchStopUpdates(
      TransitPath(
        city: saved.city.name.toLowerCase(),
        routeId: saved.conveyance.id,
        direction: saved.direction,
      ),
      silentOnError: true,
    );
  }

  Future<void> watchStopUpdates(
    TransitPath transitPath, {
    bool silentOnError = false,
  }) async {
    await _sub?.cancel();
    emit(const StopUpdateConnecting());

    _sub = _stopUpdateRepo
        .watchStopUpdates(transitPath)
        .listen(
          (stopUpdates) => emit(StopUpdateLive(stopUpdates)),
          onError: (e) => emit(
            silentOnError ? const StopUpdateIdle() : StopUpdateError(e.toString()),
          ),
        );
  }

  void stop() {
    _sub?.cancel();
    emit(const StopUpdateIdle());
  }

  @override
  Future<void> close() {
    _sub?.cancel();
    return super.close();
  }
}
