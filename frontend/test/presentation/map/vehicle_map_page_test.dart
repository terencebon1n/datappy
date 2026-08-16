import 'dart:async';

import 'package:flutter/material.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:latlong2/latlong.dart';

import 'package:frontend/application/route_selection/cubit.dart';
import 'package:frontend/application/vehicle_map/cubit.dart';
import 'package:frontend/domain/coordinates.dart';
import 'package:frontend/domain/route_geometry.dart';
import 'package:frontend/domain/transit_path.dart';
import 'package:frontend/presentation/map/vehicle_map_page.dart';

import '../../helpers/fakes.dart';
import '../../helpers/pump.dart';

TransitPath _path() => TransitPath(
      city: 'montpellier',
      routeId: 'T1',
      direction: sampleDirection(),
    );

Future<RouteSelectionCubit> _withLine(WidgetTester tester) =>
    setUpAsync(tester, () async {
      final cubit = RouteSelectionCubit(
        cityRepo: FakeCityRepo(cities: [sampleCity('Montpellier')]),
        conveyanceRepo: FakeConveyanceRepo(conveyances: [sampleConveyance()]),
        stopRepo: FakeStopNameRepo(stops: const ['A', 'B']),
        directionRepo: FakeDirectionRepo(),
        selectionStore: InMemorySelectionStore(),
      );
      await Future<void>.delayed(Duration.zero);
      cubit.selectCity(sampleCity('Montpellier'));
      await Future<void>.delayed(Duration.zero);
      cubit.selectConveyance(sampleConveyance());
      await Future<void>.delayed(Duration.zero);
      return cubit;
    });

Future<TestCubits> _pump(
  WidgetTester tester, {
  RouteSelectionCubit? route,
  VehicleMapCubit? vehicleMap,
}) async {
  final cubits = TestCubits(routeSelection: route, vehicleMap: vehicleMap);
  addTearDown(cubits.close);
  await pumpApp(tester, Scaffold(body: VehicleMapPage()), cubits: cubits);
  await tester.pump();
  return cubits;
}

void main() {
  group('boundsFor', () {
    test('returns null without geometry', () {
      expect(boundsFor(null), isNull);
      expect(boundsFor(const RouteGeometry(shapes: [], stops: [])), isNull);
    });

    test('returns null when shapes carry no points', () {
      expect(
        boundsFor(const RouteGeometry(
          shapes: [RouteShape(directionId: 0, points: [])],
          stops: [],
        )),
        isNull,
      );
    });

    test('spans every shape point', () {
      final bounds = boundsFor(const RouteGeometry(
        shapes: [
          RouteShape(directionId: 0, points: [
            Coordinates(latitude: 43.60, longitude: 3.87),
            Coordinates(latitude: 43.62, longitude: 3.89),
          ]),
        ],
        stops: [],
      ));

      expect(bounds, isNotNull);
      expect(bounds!.south, 43.60);
      expect(bounds.north, 43.62);
      expect(bounds.contains(const LatLng(43.61, 3.88)), isTrue);
    });
  });

  testWidgets('invites the user to pick a line when none is selected',
      (tester) async {
    await _pump(tester);

    expect(find.textContaining('Choisissez une ligne'), findsOneWidget);
    expect(find.byType(FlutterMap), findsNothing);
  });

  testWidgets('shows a spinner while the geometry loads', (tester) async {
    final route = await _withLine(tester);
    final gate = Completer<void>();
    final vehicleMap = VehicleMapCubit(
      vehicleRepo: FakeVehiclePositionRepo(),
      geometryRepo: FakeRouteGeometryRepo(gate: gate.future),
    );
    vehicleMap.watch(_path());

    await _pump(tester, route: route, vehicleMap: vehicleMap);

    expect(find.byType(CircularProgressIndicator), findsOneWidget);
    expect(find.byType(FlutterMap), findsNothing);

    gate.complete();
  });

  testWidgets('reports a failed load', (tester) async {
    final route = await _withLine(tester);
    final vehicleMap = VehicleMapCubit(
      vehicleRepo: FakeVehiclePositionRepo(),
      geometryRepo: FakeRouteGeometryRepo(throwError: true),
    );
    await tester.runAsync(() => vehicleMap.watch(_path()));

    await _pump(tester, route: route, vehicleMap: vehicleMap);

    expect(find.textContaining('Impossible de charger'), findsOneWidget);
  });

  testWidgets('draws the route polyline, stops and vehicles', (tester) async {
    final route = await _withLine(tester);
    final vehicles = FakeVehiclePositionRepo();
    final vehicleMap = VehicleMapCubit(
      vehicleRepo: vehicles,
      geometryRepo: FakeRouteGeometryRepo(),
    );
    await tester.runAsync(() => vehicleMap.watch(_path()));
    vehicles.controller.add([
      sampleVehiclePosition(id: 'v1'),
      sampleVehiclePosition(id: 'v2', latitude: 43.61),
    ]);
    await tester.runAsync(() => Future<void>.delayed(Duration.zero));

    await _pump(tester, route: route, vehicleMap: vehicleMap);

    expect(find.byType(FlutterMap), findsOneWidget);
    expect(find.byType(PolylineLayer), findsOneWidget);
    expect(find.text('2 véhicules'), findsOneWidget);
  });

  testWidgets('counts a single vehicle in the singular', (tester) async {
    final route = await _withLine(tester);
    final vehicles = FakeVehiclePositionRepo();
    final vehicleMap = VehicleMapCubit(
      vehicleRepo: vehicles,
      geometryRepo: FakeRouteGeometryRepo(),
    );
    await tester.runAsync(() => vehicleMap.watch(_path()));
    vehicles.controller.add([sampleVehiclePosition()]);
    await tester.runAsync(() => Future<void>.delayed(Duration.zero));

    await _pump(tester, route: route, vehicleMap: vehicleMap);

    expect(find.text('1 véhicule'), findsOneWidget);
  });

  testWidgets('names the selected line in the header', (tester) async {
    final route = await _withLine(tester);
    final vehicleMap = VehicleMapCubit(
      vehicleRepo: FakeVehiclePositionRepo(),
      geometryRepo: FakeRouteGeometryRepo(),
    );
    await tester.runAsync(() => vehicleMap.watch(_path()));

    await _pump(tester, route: route, vehicleMap: vehicleMap);

    expect(find.text('Ligne T1'), findsOneWidget);
  });

  testWidgets('renders a map with no geometry to fit', (tester) async {
    final route = await _withLine(tester);
    final vehicleMap = VehicleMapCubit(
      vehicleRepo: FakeVehiclePositionRepo(),
      geometryRepo: FakeRouteGeometryRepo(
        geometry: const RouteGeometry(shapes: [], stops: []),
      ),
    );
    await tester.runAsync(() => vehicleMap.watch(_path()));

    await _pump(tester, route: route, vehicleMap: vehicleMap);

    expect(find.byType(FlutterMap), findsOneWidget);
  });
}
