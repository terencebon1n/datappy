import 'dart:async';

import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:frontend/domain/transit_path.dart' show TransitPath;
import 'package:frontend/domain/repositories/i_alert.dart' show IAlertRepository;
import 'package:frontend/domain/repositories/i_selection_store.dart' show ISelectionStore;
import 'state.dart';


class AlertCubit extends Cubit<AlertState> {
  final IAlertRepository _alertRepo;
  final ISelectionStore _selectionStore;

  TransitPath? _current;
  Timer? _refreshTimer;

  static const _refreshInterval = Duration(minutes: 1);

  AlertCubit({
    required IAlertRepository alertRepo,
    required ISelectionStore selectionStore,
  })  : _alertRepo = alertRepo,
        _selectionStore = selectionStore,
        super(const AlertIdle()) {
    _restore();
  }

  Future<void> _restore() async {
    final saved = await _selectionStore.load();
    if (saved == null) return;
    await watchAlerts(
      TransitPath(
        city: saved.city.name.toLowerCase(),
        routeId: saved.conveyance.id,
        direction: saved.direction,
      ),
    );
  }

  Future<void> watchAlerts(TransitPath transitPath) async {
    _current = transitPath;
    emit(const AlertLoading());
    await _fetch();
    _refreshTimer?.cancel();
    _refreshTimer = Timer.periodic(_refreshInterval, (_) => _fetch());
  }

  Future<void> _fetch() async {
    final path = _current;
    if (path == null) return;
    try {
      final alerts = await _alertRepo.resolveAlerts(path);
      if (isClosed || _current != path) return;
      emit(AlertLoaded(alerts));
    } catch (e) {
      if (isClosed || _current != path) return;
      emit(AlertError(e.toString()));
    }
  }

  void stop() {
    _current = null;
    _refreshTimer?.cancel();
    emit(const AlertIdle());
  }

  @override
  Future<void> close() {
    _refreshTimer?.cancel();
    return super.close();
  }
}
