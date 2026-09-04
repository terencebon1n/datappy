import 'package:flutter_test/flutter_test.dart';

import 'package:frontend/application/vehicle_map/cubit.dart';
import 'package:frontend/application/vehicle_map/state.dart';
import 'package:frontend/domain/route_geometry.dart';

import '../helpers/fakes.dart';

final _montpellier = sampleCity('Montpellier');
final _t1 = sampleConveyance(id: 'T1', shortName: '1');
final _t4 = sampleConveyance(id: 'T4', shortName: '4');

VehicleMapCubit _cubit({
  FakeVehiclePositionRepo? vehicles,
  FakeRouteGeometryRepo? geometry,
  FakeConveyanceRepo? conveyances,
}) =>
    VehicleMapCubit(
      vehicleRepo: vehicles ?? FakeVehiclePositionRepo(),
      geometryRepo: geometry ?? FakeRouteGeometryRepo(),
      conveyanceRepo:
          conveyances ?? FakeConveyanceRepo(conveyances: [_t1, _t4]),
    );

void main() {
  test('starts idle with nothing selected', () {
    final cubit = _cubit();
    addTearDown(cubit.close);

    expect(cubit.state.status, VehicleMapStatus.idle);
    expect(cubit.state.line, isNull);
    expect(cubit.state.lines, isEmpty);
    expect(cubit.state.canPickLine, isFalse);
    expect(cubit.city, isNull);
  });

  group('open', () {
    test('loads the pickable lines for the city', () async {
      final conveyances = FakeConveyanceRepo(conveyances: [_t1, _t4]);
      final cubit = _cubit(conveyances: conveyances);
      addTearDown(cubit.close);

      await cubit.open(city: _montpellier);

      expect(cubit.state.lines.map((l) => l.id), ['T1', 'T4']);
      expect(cubit.state.canPickLine, isTrue);
      expect(conveyances.calls.single.name, 'Montpellier');
      expect(cubit.city, _montpellier);
    });

    test('does nothing without a city', () async {
      final conveyances = FakeConveyanceRepo();
      final cubit = _cubit(conveyances: conveyances);
      addTearDown(cubit.close);

      await cubit.open(city: null, fallbackLine: _t1);

      expect(conveyances.calls, isEmpty);
      expect(cubit.state.line, isNull);
    });

    test('seeds the fallback line when nothing is selected yet', () async {
      final cubit = _cubit();
      addTearDown(cubit.close);

      await cubit.open(city: _montpellier, fallbackLine: _t1);

      expect(cubit.state.line?.id, 'T1');
      expect(cubit.state.status, VehicleMapStatus.live);
    });

    test('never overrides a line the user picked on the map', () async {
      final cubit = _cubit();
      addTearDown(cubit.close);

      await cubit.open(city: _montpellier, fallbackLine: _t1);
      await cubit.selectLine(_t4);
      await cubit.open(city: _montpellier, fallbackLine: _t1);

      expect(cubit.state.line?.id, 'T4');
    });

    test('reloads lines when the city changes', () async {
      final conveyances = FakeConveyanceRepo(conveyances: [_t1]);
      final cubit = _cubit(conveyances: conveyances);
      addTearDown(cubit.close);

      await cubit.open(city: _montpellier);
      await cubit.open(city: sampleCity('Nimes'));

      expect(conveyances.calls.map((c) => c.name), ['Montpellier', 'Nimes']);
    });

    test('does not refetch lines for the same city', () async {
      final conveyances = FakeConveyanceRepo(conveyances: [_t1]);
      final cubit = _cubit(conveyances: conveyances);
      addTearDown(cubit.close);

      await cubit.open(city: _montpellier);
      await cubit.open(city: _montpellier);

      expect(conveyances.calls, hasLength(1));
    });

    test('a failed line lookup leaves the picker empty', () async {
      final cubit = _cubit(conveyances: FakeConveyanceRepo(throwError: true));
      addTearDown(cubit.close);

      await cubit.open(city: _montpellier);

      expect(cubit.state.lines, isEmpty);
      expect(cubit.state.canPickLine, isFalse);
    });
  });

  group('selectLine', () {
    test('loads the geometry then subscribes to positions', () async {
      final vehicles = FakeVehiclePositionRepo();
      final geometry = FakeRouteGeometryRepo();
      final cubit = _cubit(vehicles: vehicles, geometry: geometry);
      addTearDown(cubit.close);

      await cubit.open(city: _montpellier);
      await cubit.selectLine(_t1);

      expect(geometry.calls, ['T1']);
      expect(vehicles.calls.single.routeId, 'T1');
      expect(vehicles.calls.single.city, 'montpellier');
      expect(cubit.state.geometry, isNotNull);
    });

    test('is ignored before a city is known', () async {
      final geometry = FakeRouteGeometryRepo();
      final cubit = _cubit(geometry: geometry);
      addTearDown(cubit.close);

      await cubit.selectLine(_t1);

      expect(geometry.calls, isEmpty);
      expect(cubit.state.line, isNull);
    });

    test('switching line reloads geometry and resubscribes', () async {
      final vehicles = FakeVehiclePositionRepo();
      final geometry = FakeRouteGeometryRepo();
      final cubit = _cubit(vehicles: vehicles, geometry: geometry);
      addTearDown(cubit.close);

      await cubit.open(city: _montpellier);
      await cubit.selectLine(_t1);
      await cubit.selectLine(_t4);

      expect(geometry.calls, ['T1', 'T4']);
      expect(vehicles.calls.map((c) => c.routeId), ['T1', 'T4']);
      expect(cubit.state.line?.id, 'T4');
    });

    test('switching line clears the previous vehicles', () async {
      final vehicles = FakeVehiclePositionRepo();
      final cubit = _cubit(vehicles: vehicles);
      addTearDown(cubit.close);

      await cubit.open(city: _montpellier);
      await cubit.selectLine(_t1);
      vehicles.controller.add([sampleVehiclePosition()]);
      await Future<void>.delayed(Duration.zero);
      await cubit.selectLine(_t4);

      expect(cubit.state.vehicles, isEmpty);
    });

    test('reselecting the same line does not resubscribe', () async {
      final vehicles = FakeVehiclePositionRepo();
      final geometry = FakeRouteGeometryRepo();
      final cubit = _cubit(vehicles: vehicles, geometry: geometry);
      addTearDown(cubit.close);

      await cubit.open(city: _montpellier);
      await cubit.selectLine(_t1);
      await cubit.selectLine(_t1);

      expect(geometry.calls, ['T1']);
      expect(vehicles.calls, hasLength(1));
    });

    test('keeps the pickable lines across a switch', () async {
      final cubit = _cubit();
      addTearDown(cubit.close);

      await cubit.open(city: _montpellier);
      await cubit.selectLine(_t1);

      expect(cubit.state.lines, hasLength(2));
    });

    test('goes live when positions arrive', () async {
      final vehicles = FakeVehiclePositionRepo();
      final cubit = _cubit(vehicles: vehicles);
      addTearDown(cubit.close);

      await cubit.open(city: _montpellier, fallbackLine: _t1);
      vehicles.controller.add([sampleVehiclePosition(id: 'v1')]);
      await Future<void>.delayed(Duration.zero);

      expect(cubit.state.status, VehicleMapStatus.live);
      expect(cubit.state.vehicles.single.id, 'v1');
      expect(cubit.state.geometry, isNotNull);
    });
  });

  group('failures', () {
    test('errors when the geometry cannot be loaded and never subscribes',
        () async {
      final vehicles = FakeVehiclePositionRepo();
      final cubit = _cubit(
        vehicles: vehicles,
        geometry: FakeRouteGeometryRepo(throwError: true),
      );
      addTearDown(cubit.close);

      await cubit.open(city: _montpellier, fallbackLine: _t1);

      expect(cubit.state.status, VehicleMapStatus.error);
      expect(cubit.state.line?.id, 'T1');
      expect(vehicles.calls, isEmpty);
    });

    test('errors when subscribing throws', () async {
      final cubit = _cubit(
        vehicles: FakeVehiclePositionRepo(throwOnSubscribe: true),
      );
      addTearDown(cubit.close);

      await cubit.open(city: _montpellier, fallbackLine: _t1);

      expect(cubit.state.status, VehicleMapStatus.error);
    });

    test('errors when the stream fails', () async {
      final vehicles = FakeVehiclePositionRepo();
      final cubit = _cubit(vehicles: vehicles);
      addTearDown(cubit.close);

      await cubit.open(city: _montpellier, fallbackLine: _t1);
      vehicles.controller.addError(Exception('lost'));
      await Future<void>.delayed(Duration.zero);

      expect(cubit.state.status, VehicleMapStatus.error);
    });

    test('errors when the stream closes', () async {
      final vehicles = FakeVehiclePositionRepo();
      final cubit = _cubit(vehicles: vehicles);
      addTearDown(cubit.close);

      await cubit.open(city: _montpellier, fallbackLine: _t1);
      await vehicles.controller.close();
      await Future<void>.delayed(Duration.zero);

      expect(cubit.state.status, VehicleMapStatus.error);
    });

    test('a previous error is retried on the same line', () async {
      final geometry = FakeRouteGeometryRepo();
      final cubit = _cubit(
        vehicles: FakeVehiclePositionRepo(throwOnSubscribe: true),
        geometry: geometry,
      );
      addTearDown(cubit.close);

      await cubit.open(city: _montpellier, fallbackLine: _t1);
      await cubit.selectLine(_t1);

      expect(geometry.calls, ['T1', 'T1']);
    });
  });

  test('stop clears the state', () async {
    final vehicles = FakeVehiclePositionRepo();
    final cubit = _cubit(vehicles: vehicles);
    addTearDown(cubit.close);

    await cubit.open(city: _montpellier, fallbackLine: _t1);
    vehicles.controller.add([sampleVehiclePosition()]);
    await Future<void>.delayed(Duration.zero);
    await cubit.stop();

    expect(cubit.state.status, VehicleMapStatus.idle);
    expect(cubit.state.vehicles, isEmpty);
    expect(cubit.state.geometry, isNull);
    expect(cubit.state.line, isNull);
    expect(cubit.city, isNull);
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
