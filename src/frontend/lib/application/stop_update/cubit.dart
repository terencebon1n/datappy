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
  bool _silentOnError = false;

  Timer? _watchdog;
  static const _silenceTimeout = Duration(seconds: 35);
  static const _maxBackoffSeconds = 5;

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
    _silentOnError = silentOnError;
    _reconnectTimer?.cancel();
    _reconnectAttempt = 0;
    emit(const StopUpdateConnecting());
    await _subscribe(transitPath);
  }

  Future<void> _subscribe(TransitPath path) async {
    await _sub?.cancel();
    _watchdog?.cancel();

    try {
      _sub = _stopUpdateRepo.watchStopUpdates(path).listen(
            (stopUpdates) {
              _reconnectAttempt = 0;
              _silentOnError = false;
              _armWatchdog();
              emit(StopUpdateLive(stopUpdates));
            },
            onError: (e) => _scheduleReconnect(),
            onDone: () => _scheduleReconnect(),
          );
      _armWatchdog();
    } catch (_) {
      _scheduleReconnect();
    }
  }

  void _armWatchdog() {
    _watchdog?.cancel();
    _watchdog = Timer(_silenceTimeout, () {
      _sub?.cancel();
      _scheduleReconnect();
    });
  }

  void _scheduleReconnect() {
    if (_current == null || (_reconnectTimer?.isActive ?? false)) return;
    _watchdog?.cancel();

    if (!_silentOnError) {
      emit(const StopUpdateError('Connexion perdue, reconnexion…'));
    }

    final delay = Duration(
      seconds: min(_maxBackoffSeconds, 1 << min(_reconnectAttempt, 4)),
    );
    _reconnectAttempt++;
    _reconnectTimer = Timer(delay, () {
      final path = _current;
      if (path != null) _subscribe(path);
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
