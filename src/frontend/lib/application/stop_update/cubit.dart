import 'dart:async';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:frontend/domain/transit_path.dart' show TransitPath;
import 'package:frontend/domain/repositories/i_stop_update.dart' show IStopUpdateRepository;
import 'state.dart';


class StopUpdateCubit extends Cubit<StopUpdateState> {
  final IStopUpdateRepository _stopUpdateRepo;
  StreamSubscription? _sub;

  StopUpdateCubit({required IStopUpdateRepository stopUpdateRepo})
      : _stopUpdateRepo = stopUpdateRepo,
        super(const StopUpdateIdle());

  Future<void> watchStopUpdates(TransitPath transitPath) async {
    await _sub?.cancel();
    emit(const StopUpdateConnecting());

    _sub = _stopUpdateRepo
        .watchStopUpdates(transitPath)
        .listen(
          (stopUpdates) => emit(StopUpdateLive(stopUpdates)),
          onError: (e) => emit(StopUpdateError(e.toString())),
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
