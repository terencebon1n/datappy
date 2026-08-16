import 'package:flutter_test/flutter_test.dart';

import 'package:frontend/application/vehicle_map/cubit.dart';
import 'package:frontend/application/vehicle_map/state.dart';
import 'package:frontend/domain/route_geometry.dart';
import 'package:frontend/domain/transit_path.dart';

import '../helpers/fakes.dart';

VehicleMapCubit _cubit({
  FakeVehiclePositionRepo? vehicles,
  FakeRouteGeometryRepo? geometry,
}) =>
    VehicleMapCubit(
      vehicleRepo: vehicles ?? FakeVehiclePositionRepo(),
      geometryRepo: geometry ?? FakeRouteGeometryRepo(),
    );

TransitPath _path({String routeId = 'T1'}) => TransitPath(
      city: 'montpellier',
      routeId: routeId,
      direction: sampleDirection(),
    );

void main() {
  test('starts idle', () {
    final cubit = _cubit();
    addTearDown(cubit.close);

    expect(cubit.state.status, VehicleMapStatus.idle);
    expect(cubit.state.vehicles, isEmpty);
    expect(cubit.state.geometry, isNull);
  });

  test('loads the route geometry then subscribes to positions', () async {
    final vehicles = FakeVehiclePositionRepo();
    final geometry = FakeRouteGeometryRepo();
    final cubit = _cubit(vehicles: vehicles, geometry: geometry);
    addTearDown(cubit.close);

    await cubit.watch(_path());

    expect(geometry.calls, ['T1']);
    expect(vehicles.calls.single.routeId, 'T1');
    expect(cubit.state.geometry, isNotNull);
    expect(cubit.state.geometry!.stops.single.name, 'Comédie');
  });

  test('goes live when positions arrive', () async {
    final vehicles = FakeVehiclePositionRepo();
    final cubit = _cubit(vehicles: vehicles);
    addTearDown(cubit.close);

    await cubit.watch(_path());
    vehicles.controller.add([sampleVehiclePosition(id: 'v1')]);
    await Future<void>.delayed(Duration.zero);

    expect(cubit.state.status, VehicleMapStatus.live);
    expect(cubit.state.vehicles.single.id, 'v1');
  });

  test('keeps the geometry across position updates', () async {
    final vehicles = FakeVehiclePositionRepo();
    final cubit = _cubit(vehicles: vehicles);
    addTearDown(cubit.close);

    await cubit.watch(_path());
    vehicles.controller.add([sampleVehiclePosition()]);
    await Future<void>.delayed(Duration.zero);

    expect(cubit.state.geometry, isNotNull);
  });

  test('errors when the geometry cannot be loaded and never subscribes',
      () async {
    final vehicles = FakeVehiclePositionRepo();
    final cubit = _cubit(
      vehicles: vehicles,
      geometry: FakeRouteGeometryRepo(throwError: true),
    );
    addTearDown(cubit.close);

    await cubit.watch(_path());

    expect(cubit.state.status, VehicleMapStatus.error);
    expect(vehicles.calls, isEmpty);
  });

  test('errors when subscribing throws', () async {
    final cubit = _cubit(vehicles: FakeVehiclePositionRepo(throwOnSubscribe: true));
    addTearDown(cubit.close);

    await cubit.watch(_path());

    expect(cubit.state.status, VehicleMapStatus.error);
  });

  test('errors when the stream fails', () async {
    final vehicles = FakeVehiclePositionRepo();
    final cubit = _cubit(vehicles: vehicles);
    addTearDown(cubit.close);

    await cubit.watch(_path());
    vehicles.controller.addError(Exception('lost'));
    await Future<void>.delayed(Duration.zero);

    expect(cubit.state.status, VehicleMapStatus.error);
  });

  test('errors when the stream closes', () async {
    final vehicles = FakeVehiclePositionRepo();
    final cubit = _cubit(vehicles: vehicles);
    addTearDown(cubit.close);

    await cubit.watch(_path());
    await vehicles.controller.close();
    await Future<void>.delayed(Duration.zero);

    expect(cubit.state.status, VehicleMapStatus.error);
  });

  test('watching the same route twice does not resubscribe', () async {
    final vehicles = FakeVehiclePositionRepo();
    final geometry = FakeRouteGeometryRepo();
    final cubit = _cubit(vehicles: vehicles, geometry: geometry);
    addTearDown(cubit.close);

    await cubit.watch(_path());
    await cubit.watch(_path());

    expect(geometry.calls, ['T1']);
    expect(vehicles.calls, hasLength(1));
  });

  test('switching route reloads geometry and resubscribes', () async {
    final vehicles = FakeVehiclePositionRepo();
    final geometry = FakeRouteGeometryRepo();
    final cubit = _cubit(vehicles: vehicles, geometry: geometry);
    addTearDown(cubit.close);

    await cubit.watch(_path(routeId: 'T1'));
    await cubit.watch(_path(routeId: 'T4'));

    expect(geometry.calls, ['T1', 'T4']);
    expect(vehicles.calls.map((c) => c.routeId), ['T1', 'T4']);
  });

  test('a previous error is retried on the same route', () async {
    final vehicles = FakeVehiclePositionRepo(throwOnSubscribe: true);
    final geometry = FakeRouteGeometryRepo();
    final cubit = _cubit(vehicles: vehicles, geometry: geometry);
    addTearDown(cubit.close);

    await cubit.watch(_path());
    await cubit.watch(_path());

    expect(geometry.calls, ['T1', 'T1']);
  });

  test('stop clears the state', () async {
    final vehicles = FakeVehiclePositionRepo();
    final cubit = _cubit(vehicles: vehicles);
    addTearDown(cubit.close);

    await cubit.watch(_path());
    vehicles.controller.add([sampleVehiclePosition()]);
    await Future<void>.delayed(Duration.zero);
    await cubit.stop();

    expect(cubit.state.status, VehicleMapStatus.idle);
    expect(cubit.state.vehicles, isEmpty);
    expect(cubit.state.geometry, isNull);
  });

  test('state copyWith keeps untouched fields', () {
    const state = VehicleMapState(status: VehicleMapStatus.live);

    final copy = state.copyWith(vehicles: [sampleVehiclePosition()]);

    expect(copy.status, VehicleMapStatus.live);
    expect(copy.vehicles, hasLength(1));
  });

  test('route geometry reports emptiness', () {
    const empty = RouteGeometry(shapes: [], stops: []);

    expect(empty.isEmpty, isTrue);
    expect(sampleRouteGeometry().isEmpty, isFalse);
  });
}
