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

  /// The path currently being watched, kept so the feed can be re-established
  /// after a socket drop or when the app returns to the foreground.
  TransitPath? _current;
  Timer? _reconnectTimer;
  int _reconnectAttempt = 0;

  StopUpdateCubit({
    required IStopUpdateRepository stopUpdateRepo,
    required ISelectionStore selectionStore,
  })  : _stopUpdateRepo = stopUpdateRepo,
        _selectionStore = selectionStore,
        super(const StopUpdateIdle()) {
    WidgetsBinding.instance.addObserver(this);
    _restore();
  }

  /// If a previous selection was persisted, reconnect its live feed on launch.
  /// A failed reconnect falls back silently to idle (no error banner) and keeps
  /// retrying. The path is built the same way the funnel does it when a search
  /// completes.
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

  /// Starts (or restarts) the live feed for [transitPath]. This is the
  /// user-initiated entry point: it resets the reconnect backoff and cancels any
  /// pending reconnect before connecting.
  Future<void> watchStopUpdates(
    TransitPath transitPath, {
    bool silentOnError = false,
  }) async {
    _current = transitPath;
    _reconnectTimer?.cancel();
    _reconnectAttempt = 0;
    await _subscribe(transitPath, silentOnError: silentOnError);
  }

  /// Opens a fresh websocket subscription for [path]. Shared by the
  /// user-initiated [watchStopUpdates], the automatic reconnect timer and the
  /// resume handler. A closed (`onDone`) or errored stream schedules a
  /// reconnect so a silently-dropped socket self-heals.
  Future<void> _subscribe(
    TransitPath path, {
    bool silentOnError = false,
  }) async {
    await _sub?.cancel();
    // Avoid flashing the connecting state over live data on an automatic retry.
    if (state is! StopUpdateLive) emit(const StopUpdateConnecting());

    _sub = _stopUpdateRepo.watchStopUpdates(path).listen(
          (stopUpdates) {
            _reconnectAttempt = 0;
            emit(StopUpdateLive(stopUpdates));
          },
          onError: (e) => _scheduleReconnect(silentOnError),
          onDone: () => _scheduleReconnect(silentOnError),
        );
  }

  /// Schedules a reconnect with capped exponential backoff. No-op if a
  /// reconnect is already pending or there is no active selection.
  void _scheduleReconnect(bool silentOnError) {
    if (_current == null || (_reconnectTimer?.isActive ?? false)) return;

    // Surface the drop only when not silent and not already showing live data,
    // so a restored feed keeps its last departures while it retries.
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
    // On resume the previous socket may have been torn down while the app was
    // backgrounded; re-establish the feed immediately for the active selection.
    if (state == AppLifecycleState.resumed && _current != null) {
      _reconnectTimer?.cancel();
      _reconnectAttempt = 0;
      _subscribe(_current!);
    }
  }

  void stop() {
    _current = null;
    _reconnectTimer?.cancel();
    _sub?.cancel();
    emit(const StopUpdateIdle());
  }

  @override
  Future<void> close() {
    WidgetsBinding.instance.removeObserver(this);
    _reconnectTimer?.cancel();
    _sub?.cancel();
    return super.close();
  }
}
