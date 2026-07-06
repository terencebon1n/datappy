import 'dart:async';

import 'package:fake_async/fake_async.dart';
import 'package:flutter_test/flutter_test.dart';

import 'package:frontend/application/stop_update/cubit.dart';
import 'package:frontend/application/stop_update/state.dart';
import 'package:frontend/domain/direction.dart';
import 'package:frontend/domain/stop_update.dart';
import 'package:frontend/domain/transit_path.dart';
import 'package:frontend/domain/saved_selection.dart';
import 'package:frontend/domain/repositories/i_stop_update.dart';
import 'package:frontend/domain/repositories/i_selection_store.dart';

class _NullStore implements ISelectionStore {
  @override
  Future<SavedSelection?> load() async => null;
  @override
  Future<void> save(SavedSelection s) async {}
}

/// Each call to [watchStopUpdates] returns a fresh controller. The first
/// [failFirst] calls error+close (simulating a backend that is down / restarting);
/// every call after that emits an empty live payload (backend back up).
class _FakeRepo implements IStopUpdateRepository {
  _FakeRepo({required this.failFirst});
  final int failFirst;
  int calls = 0;

  @override
  Stream<List<StopUpdate>> watchStopUpdates(TransitPath transitPath) {
    final i = calls++;
    final controller = StreamController<List<StopUpdate>>();
    scheduleMicrotask(() {
      if (i < failFirst) {
        controller.addError(Exception('connection refused'));
        controller.close();
      } else {
        controller.add(<StopUpdate>[]);
      }
    });
    return controller.stream;
  }
}

TransitPath _path() => TransitPath(
      city: 'lyon',
      routeId: 'T1',
      direction: Direction(
        directionId: 0,
        stopIdOrigin: 'o',
        stopIdDestination: 'd',
      ),
    );

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  test('auto-reconnects to Live after a transient failure, no new search', () {
    fakeAsync((async) {
      final repo = _FakeRepo(failFirst: 1);
      final cubit = StopUpdateCubit(
        stopUpdateRepo: repo,
        selectionStore: _NullStore(),
      );

      cubit.watchStopUpdates(_path());
      async.flushMicrotasks();

      expect(cubit.state, isA<StopUpdateError>(),
          reason: 'first connection fails -> error shown');

      // Let the reconnect backoff timer fire (first retry is ~1s).
      async.elapse(const Duration(seconds: 6));
      async.flushMicrotasks();

      expect(cubit.state, isA<StopUpdateLive>(),
          reason: 'should reconnect on its own once the backend is back');

      expect(repo.calls, greaterThanOrEqualTo(2),
          reason: 'the cubit must retry the websocket without a new search');

      cubit.close();
    });
  });

  test('keeps retrying through several failures then recovers', () {
    fakeAsync((async) {
      final repo = _FakeRepo(failFirst: 4);
      final cubit = StopUpdateCubit(
        stopUpdateRepo: repo,
        selectionStore: _NullStore(),
      );

      cubit.watchStopUpdates(_path());
      async.flushMicrotasks();

      // Enough wall-clock for 4 failed attempts at the capped backoff.
      async.elapse(const Duration(seconds: 30));
      async.flushMicrotasks();

      expect(cubit.state, isA<StopUpdateLive>());
      cubit.close();
    });
  });
}
