import 'package:fake_async/fake_async.dart';
import 'package:flutter_test/flutter_test.dart';

import 'package:frontend/application/alert/cubit.dart';
import 'package:frontend/application/alert/state.dart';

import '../helpers/fakes.dart';

AlertCubit _cubit(FakeAlertRepo repo, {InMemorySelectionStore? store}) => AlertCubit(
      alertRepo: repo,
      selectionStore: store ?? InMemorySelectionStore(),
    );

void main() {
  test('starts idle when nothing is stored', () async {
    final cubit = _cubit(FakeAlertRepo());
    expect(cubit.state, isA<AlertIdle>());
    await cubit.close();
  });

  test('restores the saved selection on creation', () async {
    final repo = FakeAlertRepo(alerts: [sampleAlert()]);
    final cubit = _cubit(repo, store: InMemorySelectionStore(sampleSelection()));

    await Future<void>.delayed(Duration.zero);

    expect(repo.calls.single.routeId, 'T1');
    expect(cubit.state, isA<AlertLoaded>());
    cubit.stop();
    await cubit.close();
  });

  test('emits loaded alerts for the watched path', () async {
    final repo = FakeAlertRepo(alerts: [sampleAlert(), sampleAlert(id: 'a2')]);
    final cubit = _cubit(repo);

    await cubit.watchAlerts(sampleTransitPath());

    final state = cubit.state as AlertLoaded;
    expect(state.alerts, hasLength(2));
    expect(repo.calls.single.city, 'lyon');
    cubit.stop();
    await cubit.close();
  });

  test('emits an error when the repository throws', () async {
    final cubit = _cubit(FakeAlertRepo(throwError: true));

    await cubit.watchAlerts(sampleTransitPath());

    expect(cubit.state, isA<AlertError>());
    cubit.stop();
    await cubit.close();
  });

  test('stop clears the state back to idle', () async {
    final cubit = _cubit(FakeAlertRepo(alerts: [sampleAlert()]));
    await cubit.watchAlerts(sampleTransitPath());

    cubit.stop();

    expect(cubit.state, isA<AlertIdle>());
    await cubit.close();
  });

  test('a stale in-flight response is discarded after stop', () async {
    final repo = FakeAlertRepo(alerts: [sampleAlert()]);
    final cubit = _cubit(repo);

    final pending = cubit.watchAlerts(sampleTransitPath());
    cubit.stop();
    await pending;

    expect(cubit.state, isA<AlertIdle>());
    await cubit.close();
  });

  test('a stale in-flight failure is discarded after stop', () async {
    final repo = FakeAlertRepo(throwError: true);
    final cubit = _cubit(repo);

    final pending = cubit.watchAlerts(sampleTransitPath());
    cubit.stop();
    await pending;

    expect(cubit.state, isA<AlertIdle>());
    await cubit.close();
  });

  test('the periodic refresh re-queries the repository', () {
    fakeAsync((async) {
      final repo = FakeAlertRepo(alerts: [sampleAlert()]);
      final cubit = _cubit(repo);

      cubit.watchAlerts(sampleTransitPath());
      async.flushMicrotasks();
      expect(repo.calls, hasLength(1));

      async.elapse(const Duration(minutes: 1));
      async.flushMicrotasks();
      expect(repo.calls, hasLength(2));

      cubit.stop();

      async.elapse(const Duration(minutes: 1));
      async.flushMicrotasks();
      expect(repo.calls, hasLength(2));

      cubit.close();
      async.flushMicrotasks();
    });
  });
}
