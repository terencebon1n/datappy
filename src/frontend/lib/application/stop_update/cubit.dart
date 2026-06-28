import 'dart:async';
import 'dart:math' show min;
import 'package:flutter/widgets.dart' show WidgetsBinding, WidgetsBindingObserver, AppLifecycleState;
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:frontend/domain/transit_path.dart' show TransitPath;
import 'package:frontend/domain/repositories/i_stop_update.dart' show IStopUpdateRepository;
import 'package:frontend/domain/repositories/i_selection_store.dart' show ISelectionStore;
import 'state.dart';


class StopUpdateCubit extends Cubit<StopUpdateState> with WidgetsBindingObserver {
  final IStopUpdateRepository _stopUpdateRepo;
  final ISelectionStore _selectionStore;
  StreamSubscription? _sub;

  TransitPath? _current;
  Timer? _reconnectTimer;
  int _reconnectAttempt = 0;

  Timer? _watchdog;
  static const _silenceTimeout = Duration(seconds: 35);

  StopUpdateCubit({
    required IStopUpdateRepository stopUpdateRepo,
    required ISelectionStore selectionStore,
  })  : _stopUpdateRepo = stopUpdateRepo,
        _selectionStore = selectionStore,
        super(const StopUpdateIdle()) {
    WidgetsBinding.instance.addObserver(this);
    _restore();
  }

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
    _current = transitPath;
    _reconnectTimer?.cancel();
    _reconnectAttempt = 0;
    await _subscribe(transitPath, silentOnError: silentOnError);
  }

  Future<void> _subscribe(
    TransitPath path, {
    bool silentOnError = false,
  }) async {
    await _sub?.cancel();
    _watchdog?.cancel();
    if (state is! StopUpdateLive) emit(const StopUpdateConnecting());

    try {
      _sub = _stopUpdateRepo.watchStopUpdates(path).listen(
            (stopUpdates) {
              _reconnectAttempt = 0;
              _armWatchdog(silentOnError);
              emit(StopUpdateLive(stopUpdates));
            },
            onError: (e) => _scheduleReconnect(silentOnError),
            onDone: () => _scheduleReconnect(silentOnError),
          );
      _armWatchdog(silentOnError);
    } catch (_) {
      _scheduleReconnect(silentOnError);
    }
  }

  void _armWatchdog(bool silentOnError) {
    _watchdog?.cancel();
    _watchdog = Timer(_silenceTimeout, () {
      _sub?.cancel();
      _scheduleReconnect(silentOnError);
    });
  }

  void _scheduleReconnect(bool silentOnError) {
    if (_current == null || (_reconnectTimer?.isActive ?? false)) return;
    _watchdog?.cancel();

    if (!silentOnError && state is! StopUpdateLive) {
      emit(const StopUpdateError('Connexion perdue, reconnexion…'));
    }

    final delay = Duration(seconds: min(30, 1 << _reconnectAttempt));
    _reconnectAttempt++;
    _reconnectTimer = Timer(delay, () {
      final path = _current;
      if (path != null) _subscribe(path, silentOnError: silentOnError);
    });
  }

  @override
  void didChangeAppLifecycleState(AppLifecycleState state) {
    if (state == AppLifecycleState.resumed && _current != null) {
      _reconnectTimer?.cancel();
      _reconnectAttempt = 0;
      _subscribe(_current!);
    }
  }

  void stop() {
    _current = null;
    _reconnectTimer?.cancel();
    _watchdog?.cancel();
    _sub?.cancel();
    emit(const StopUpdateIdle());
  }

  @override
  Future<void> close() {
    WidgetsBinding.instance.removeObserver(this);
    _reconnectTimer?.cancel();
    _watchdog?.cancel();
    _sub?.cancel();
    return super.close();
  }
}
