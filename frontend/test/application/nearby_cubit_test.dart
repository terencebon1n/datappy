import 'package:flutter_test/flutter_test.dart';

import 'package:frontend/application/nearby/cubit.dart';
import 'package:frontend/application/nearby/state.dart';
import 'package:frontend/domain/coordinates.dart';
import 'package:frontend/domain/repositories/i_location.dart';

import '../helpers/fakes.dart';

NearbyCubit _cubit({
  FakeNearbyStopRepo? repo,
  FakeLocationProvider? location,
}) =>
    NearbyCubit(
      nearbyRepo: repo ?? FakeNearbyStopRepo(),
      location: location ?? FakeLocationProvider(),
    );

void main() {
  test('starts idle with no stops', () {
    final cubit = _cubit();
    addTearDown(cubit.close);

    expect(cubit.state.status, NearbyStatus.idle);
    expect(cubit.state.stops, isEmpty);
    expect(cubit.state.isBusy, isFalse);
  });

  test('emits locating then loading then ready', () async {
    final repo = FakeNearbyStopRepo(stops: [sampleNearbyStop()]);
    final cubit = _cubit(repo: repo);
    addTearDown(cubit.close);

    final seen = <NearbyStatus>[];
    cubit.stream.listen((s) => seen.add(s.status));

    await cubit.findNearby(sampleCity());
    await Future<void>.delayed(Duration.zero);

    expect(seen, [
      NearbyStatus.locating,
      NearbyStatus.loading,
      NearbyStatus.ready,
    ]);
    expect(cubit.state.stops.single.name, 'Comédie');
  });

  test('passes the located coordinates and radius to the repository', () async {
    final repo = FakeNearbyStopRepo();
    final cubit = _cubit(
      repo: repo,
      location: FakeLocationProvider(
        coordinates: const Coordinates(latitude: 1.5, longitude: -2.5),
      ),
    );
    addTearDown(cubit.close);

    await cubit.findNearby(sampleCity(), radiusMeters: 1200);

    expect(repo.calls.single.latitude, 1.5);
    expect(repo.calls.single.longitude, -2.5);
    expect(repo.lastRadiusMeters, 1200);
  });

  test('reports denied permission without querying the repository', () async {
    final repo = FakeNearbyStopRepo();
    final cubit = _cubit(
      repo: repo,
      location:
          FakeLocationProvider(permission: LocationPermissionStatus.denied),
    );
    addTearDown(cubit.close);

    await cubit.findNearby(sampleCity());

    expect(cubit.state.status, NearbyStatus.denied);
    expect(repo.calls, isEmpty);
  });

  test('reports a disabled location service', () async {
    final cubit = _cubit(
      location: FakeLocationProvider(
        permission: LocationPermissionStatus.serviceDisabled,
      ),
    );
    addTearDown(cubit.close);

    await cubit.findNearby(sampleCity());

    expect(cubit.state.status, NearbyStatus.serviceDisabled);
  });

  test('fails when the position cannot be read', () async {
    final cubit = _cubit(location: FakeLocationProvider(throwError: true));
    addTearDown(cubit.close);

    await cubit.findNearby(sampleCity());

    expect(cubit.state.status, NearbyStatus.failed);
  });

  test('fails when the repository throws', () async {
    final cubit = _cubit(repo: FakeNearbyStopRepo(throwError: true));
    addTearDown(cubit.close);

    await cubit.findNearby(sampleCity());

    expect(cubit.state.status, NearbyStatus.failed);
    expect(cubit.state.stops, isEmpty);
  });

  test('is busy while locating and loading', () {
    expect(const NearbyState(status: NearbyStatus.locating).isBusy, isTrue);
    expect(const NearbyState(status: NearbyStatus.loading).isBusy, isTrue);
    expect(const NearbyState(status: NearbyStatus.ready).isBusy, isFalse);
  });

  test('reset returns to idle', () async {
    final repo = FakeNearbyStopRepo(stops: [sampleNearbyStop()]);
    final cubit = _cubit(repo: repo);
    addTearDown(cubit.close);

    await cubit.findNearby(sampleCity());
    cubit.reset();

    expect(cubit.state.status, NearbyStatus.idle);
    expect(cubit.state.stops, isEmpty);
  });
}
