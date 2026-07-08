import 'dart:async';

import 'package:fake_async/fake_async.dart';
import 'package:flutter/widgets.dart' show AppLifecycleState;
import 'package:flutter_test/flutter_test.dart';

import 'package:frontend/application/stop_update/cubit.dart';
import 'package:frontend/application/stop_update/state.dart';
import 'package:frontend/domain/direction.dart';
import 'package:frontend/domain/stop_update.dart';
import 'package:frontend/domain/transit_path.dart';
import 'package:frontend/domain/repositories/i_stop_update.dart';

import '../helpers/fakes.dart';

class _ScriptedRepo implements IStopUpdateRepository {
  _ScriptedRepo(this.behaviour);
  final void Function(int call, StreamController<List<StopUpdate>> c) behaviour;
  int calls = 0;

  @override
  Stream<List<StopUpdate>> watchStopUpdates(TransitPath transitPath) {
    final i = calls++;
    final c = StreamController<List<StopUpdate>>();
    scheduleMicrotask(() => behaviour(i, c));
    return c.stream;
  }
}

class _ThrowingRepo implements IStopUpdateRepository {
  @override
  Stream<List<StopUpdate>> watchStopUpdates(TransitPath transitPath) =>
      throw StateError('cannot connect');
}

TransitPath _path() => TransitPath(
      city: 'lyon',
      routeId: 'T1',
      direction: Direction(directionId: 0, stopIdOrigin: 'o', stopIdDestination: 'd'),
    );

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  test('_restore auto-watches the saved selection and hides transient errors', () {
    fakeAsync((async) {
      final repo = _ScriptedRepo((i, c) {
        if (i == 0) {
          c.addError(Exception('backend down'));
          c.close();
        } else {
          c.add([sampleStopUpdate()]);
        }
      });
      final cubit = StopUpdateCubit(
        stopUpdateRepo: repo,
        selectionStore: InMemorySelectionStore(sampleSelection()),
      );

      async.flushMicrotasks();
      expect(cubit.state, isA<StopUpdateConnecting>(),
          reason: 'a silent restore must not surface the error');

      async.elapse(const Duration(seconds: 6));
      async.flushMicrotasks();
      expect(cubit.state, isA<StopUpdateLive>());
      expect(repo.calls, greaterThanOrEqualTo(2));

      cubit.stop();
      cubit.close();
    });
  });

  test('stop returns to idle and cancels work', () {
    fakeAsync((async) {
      final repo = _ScriptedRepo((i, c) => c.add([sampleStopUpdate()]));
      final cubit = StopUpdateCubit(
        stopUpdateRepo: repo,
        selectionStore: InMemorySelectionStore(),
      );

      cubit.watchStopUpdates(_path());
      async.flushMicrotasks();
      expect(cubit.state, isA<StopUpdateLive>());

      cubit.stop();
      expect(cubit.state, isA<StopUpdateIdle>());
      cubit.close();
    });
  });

  test('a synchronous connect failure surfaces an error', () {
    fakeAsync((async) {
      final cubit = StopUpdateCubit(
        stopUpdateRepo: _ThrowingRepo(),
        selectionStore: InMemorySelectionStore(),
      );

      cubit.watchStopUpdates(_path());
      async.flushMicrotasks();

      expect(cubit.state, isA<StopUpdateError>());
      cubit.stop();
      cubit.close();
    });
  });

  test('resubscribes after the live feed goes silent (watchdog)', () {
    fakeAsync((async) {
      final repo = _ScriptedRepo((i, c) => c.add([sampleStopUpdate()]));
      final cubit = StopUpdateCubit(
        stopUpdateRepo: repo,
        selectionStore: InMemorySelectionStore(),
      );

      cubit.watchStopUpdates(_path());
      async.flushMicrotasks();
      expect(cubit.state, isA<StopUpdateLive>());
      expect(repo.calls, 1);

      async.elapse(const Duration(seconds: 40));
      async.flushMicrotasks();
      expect(repo.calls, greaterThanOrEqualTo(2));

      cubit.stop();
      cubit.close();
    });
  });

  group('didChangeAppLifecycleState', () {
    test('resume re-subscribes while watching', () {
      fakeAsync((async) {
        final repo = _ScriptedRepo((i, c) => c.add([sampleStopUpdate()]));
        final cubit = StopUpdateCubit(
          stopUpdateRepo: repo,
          selectionStore: InMemorySelectionStore(),
        );
        cubit.watchStopUpdates(_path());
        async.flushMicrotasks();
        final before = repo.calls;

        cubit.didChangeAppLifecycleState(AppLifecycleState.resumed);
        async.flushMicrotasks();

        expect(repo.calls, before + 1);
        cubit.stop();
        cubit.close();
      });
    });

    test('resume is ignored when nothing is being watched', () async {
      final repo = _ScriptedRepo((i, c) => c.add([sampleStopUpdate()]));
      final cubit = StopUpdateCubit(
        stopUpdateRepo: repo,
        selectionStore: InMemorySelectionStore(),
      );
      await Future<void>.delayed(Duration.zero);

      cubit.didChangeAppLifecycleState(AppLifecycleState.resumed);
      expect(repo.calls, 0);
      await cubit.close();
    });

    test('non-resume states are ignored', () {
      fakeAsync((async) {
        final repo = _ScriptedRepo((i, c) => c.add([sampleStopUpdate()]));
        final cubit = StopUpdateCubit(
          stopUpdateRepo: repo,
          selectionStore: InMemorySelectionStore(),
        );
        cubit.watchStopUpdates(_path());
        async.flushMicrotasks();
        final before = repo.calls;

        cubit.didChangeAppLifecycleState(AppLifecycleState.paused);
        async.flushMicrotasks();

        expect(repo.calls, before);
        cubit.stop();
        cubit.close();
      });
    });
  });
}
