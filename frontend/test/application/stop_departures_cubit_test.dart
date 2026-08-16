import 'package:flutter_test/flutter_test.dart';

import 'package:frontend/application/stop_departures/cubit.dart';
import 'package:frontend/application/stop_departures/state.dart';

import '../helpers/fakes.dart';

void main() {
  test('starts loading with no departures', () {
    final cubit = StopDeparturesCubit(repo: FakeStopDepartureRepo());
    addTearDown(cubit.close);

    expect(cubit.state.status, StopDeparturesStatus.loading);
    expect(cubit.state.departures, isEmpty);
  });

  test('loads departures for the requested stop', () async {
    final repo = FakeStopDepartureRepo(
      departures: [sampleStopDeparture(headsign: 'Mosson')],
    );
    final cubit = StopDeparturesCubit(repo: repo);
    addTearDown(cubit.close);

    await cubit.load(routeId: 'T1', stopId: 's9', city: sampleCity());

    expect(cubit.state.status, StopDeparturesStatus.ready);
    expect(cubit.state.departures.single.headsign, 'Mosson');
    expect(repo.calls, ['s9']);
  });

  test('reports an empty stop as ready', () async {
    final cubit = StopDeparturesCubit(repo: FakeStopDepartureRepo());
    addTearDown(cubit.close);

    await cubit.load(routeId: 'T1', stopId: 's1', city: sampleCity());

    expect(cubit.state.status, StopDeparturesStatus.ready);
    expect(cubit.state.departures, isEmpty);
  });

  test('errors when the repository throws', () async {
    final cubit = StopDeparturesCubit(
      repo: FakeStopDepartureRepo(throwError: true),
    );
    addTearDown(cubit.close);

    await cubit.load(routeId: 'T1', stopId: 's1', city: sampleCity());

    expect(cubit.state.status, StopDeparturesStatus.error);
    expect(cubit.state.departures, isEmpty);
  });

  test('reloading resets to loading first', () async {
    final repo = FakeStopDepartureRepo(departures: [sampleStopDeparture()]);
    final cubit = StopDeparturesCubit(repo: repo);
    addTearDown(cubit.close);

    final seen = <StopDeparturesStatus>[];
    cubit.stream.listen((s) => seen.add(s.status));

    await cubit.load(routeId: 'T1', stopId: 's1', city: sampleCity());
    await cubit.load(routeId: 'T1', stopId: 's2', city: sampleCity());
    await Future<void>.delayed(Duration.zero);

    expect(seen, [
      StopDeparturesStatus.loading,
      StopDeparturesStatus.ready,
      StopDeparturesStatus.loading,
      StopDeparturesStatus.ready,
    ]);
  });
}
