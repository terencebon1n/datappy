import 'dart:async';

import 'package:flutter/material.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:latlong2/latlong.dart';

import 'package:frontend/application/route_selection/cubit.dart';
import 'package:frontend/application/theme/cubit.dart';
import 'package:frontend/application/stop_departures/cubit.dart';
import 'package:frontend/application/vehicle_map/cubit.dart';
import 'package:frontend/domain/coordinates.dart';
import 'package:frontend/domain/route_geometry.dart';
import 'package:frontend/presentation/map/stop_details_sheet.dart';
import 'package:frontend/presentation/map/vehicle_details_sheet.dart';
import 'package:frontend/presentation/map/vehicle_map_page.dart';
import 'package:frontend/presentation/theme/colors.dart';

import '../../helpers/fakes.dart';
import '../../helpers/pump.dart';

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

    test('a single point still yields a fittable, non-zero-area box', () {
      final bounds = boundsFor(const RouteGeometry(
        shapes: [
          RouteShape(directionId: 0, points: [
            Coordinates(latitude: 43.6, longitude: 3.87),
          ]),
        ],
        stops: [],
      ));

      expect(bounds, isNotNull);
      expect(bounds!.north - bounds.south, greaterThan(0));
      expect(bounds.east - bounds.west, greaterThan(0));
    });

    test('identical points still yield a non-zero-area box', () {
      final bounds = boundsFor(const RouteGeometry(
        shapes: [
          RouteShape(directionId: 0, points: [
            Coordinates(latitude: 43.6, longitude: 3.87),
            Coordinates(latitude: 43.6, longitude: 3.87),
          ]),
        ],
        stops: [],
      ));

      expect(bounds!.north - bounds.south, closeTo(minimumFitSpanDegrees, 1e-9));
    });

    test('a line of points is widened on the flat axis only', () {
      final bounds = boundsFor(const RouteGeometry(
        shapes: [
          RouteShape(directionId: 0, points: [
            Coordinates(latitude: 43.60, longitude: 3.87),
            Coordinates(latitude: 43.70, longitude: 3.87),
          ]),
        ],
        stops: [],
      ));

      expect(bounds!.north - bounds.south, closeTo(0.10, 1e-9));
      expect(bounds.east - bounds.west, closeTo(minimumFitSpanDegrees, 1e-9));
    });

    test('discards non-finite coordinates', () {
      final bounds = boundsFor(RouteGeometry(
        shapes: [
          RouteShape(directionId: 0, points: [
            const Coordinates(latitude: 43.60, longitude: 3.87),
            const Coordinates(latitude: 43.70, longitude: 3.89),
            Coordinates(latitude: double.nan, longitude: 3.88),
            Coordinates(latitude: double.infinity, longitude: 3.88),
          ]),
        ],
        stops: const [],
      ));

      expect(bounds!.north, closeTo(43.70, 1e-9));
      expect(bounds.south, closeTo(43.60, 1e-9));
    });

    test('discards out-of-range coordinates', () {
      final bounds = boundsFor(const RouteGeometry(
        shapes: [
          RouteShape(directionId: 0, points: [
            Coordinates(latitude: 43.60, longitude: 3.87),
            Coordinates(latitude: 43.70, longitude: 3.89),
          ]),
        ],
        stops: [],
      ));

      expect(isPlottable(const Coordinates(latitude: 91, longitude: 0)), isFalse);
      expect(isPlottable(const Coordinates(latitude: 0, longitude: 181)), isFalse);
      expect(bounds!.north, closeTo(43.70, 1e-9));
    });

    test('returns null when every point is unusable', () {
      expect(
        boundsFor(RouteGeometry(
          shapes: [
            RouteShape(directionId: 0, points: [
              Coordinates(latitude: double.nan, longitude: double.nan),
            ]),
          ],
          stops: const [],
        )),
        isNull,
      );
    });

    test('leaves a healthy box untouched', () {
      final bounds = withMinimumSpan(
        LatLngBounds(const LatLng(43.60, 3.87), const LatLng(43.70, 3.97)),
      );

      expect(bounds.north, closeTo(43.70, 1e-9));
      expect(bounds.south, closeTo(43.60, 1e-9));
      expect(bounds.east, closeTo(3.97, 1e-9));
      expect(bounds.west, closeTo(3.87, 1e-9));
    });

    test('clamps the widened box to valid latitudes', () {
      final bounds = withMinimumSpan(
        LatLngBounds(const LatLng(-90, -180), const LatLng(-90, -180)),
      );

      expect(bounds.south, greaterThanOrEqualTo(-90));
      expect(bounds.west, greaterThanOrEqualTo(-180));
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
      conveyanceRepo: FakeConveyanceRepo(conveyances: [sampleConveyance()]),
    );
    vehicleMap.open(city: sampleCity('Montpellier'), fallbackLine: sampleConveyance());

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
      conveyanceRepo: FakeConveyanceRepo(conveyances: [sampleConveyance()]),
    );
    await tester.runAsync(() => vehicleMap.open(city: sampleCity('Montpellier'), fallbackLine: sampleConveyance()));

    await _pump(tester, route: route, vehicleMap: vehicleMap);

    expect(find.textContaining('Impossible de charger'), findsOneWidget);
  });

  testWidgets('draws the route polyline, stops and vehicles', (tester) async {
    final route = await _withLine(tester);
    final vehicles = FakeVehiclePositionRepo();
    final vehicleMap = VehicleMapCubit(
      vehicleRepo: vehicles,
      geometryRepo: FakeRouteGeometryRepo(),
      conveyanceRepo: FakeConveyanceRepo(conveyances: [sampleConveyance()]),
    );
    await tester.runAsync(() => vehicleMap.open(city: sampleCity('Montpellier'), fallbackLine: sampleConveyance()));
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
      conveyanceRepo: FakeConveyanceRepo(conveyances: [sampleConveyance()]),
    );
    await tester.runAsync(() => vehicleMap.open(city: sampleCity('Montpellier'), fallbackLine: sampleConveyance()));
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
      conveyanceRepo: FakeConveyanceRepo(conveyances: [sampleConveyance()]),
    );
    await tester.runAsync(() => vehicleMap.open(city: sampleCity('Montpellier'), fallbackLine: sampleConveyance()));

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
      conveyanceRepo: FakeConveyanceRepo(conveyances: [sampleConveyance()]),
    );
    await tester.runAsync(() => vehicleMap.open(city: sampleCity('Montpellier'), fallbackLine: sampleConveyance()));

    await _pump(tester, route: route, vehicleMap: vehicleMap);

    expect(find.byType(FlutterMap), findsOneWidget);
  });

  group('basemapUrl', () {
    test('serves the light basemap in light mode', () {
      expect(basemapUrl(isDark: false), contains('light_all'));
    });

    test('serves the dark basemap in dark mode', () {
      expect(basemapUrl(isDark: true), contains('dark_all'));
    });

    test('keeps the retina placeholder', () {
      expect(basemapUrl(isDark: false), contains('{r}'));
      expect(basemapUrl(isDark: true), contains('{r}'));
    });
  });

  group('readableRouteColor', () {
    test('keeps a route colour with enough contrast', () {
      TransitColors.apply(false);
      final line = sampleConveyance(colorValue: 0xFF0080C0);

      expect(readableRouteColor(line, isDark: false), const Color(0xFF0080C0));
    });

    test('replaces a near-black route colour on the dark basemap', () {
      TransitColors.apply(true);
      final line = sampleConveyance(colorValue: 0xFF000000);

      expect(readableRouteColor(line, isDark: true), TransitColors.accent);
    });

    test('replaces a near-white route colour on the light basemap', () {
      TransitColors.apply(false);
      final line = sampleConveyance(colorValue: 0xFFFFFFFF);

      expect(readableRouteColor(line, isDark: false), TransitColors.accent);
    });

    test('keeps a near-black route colour on the light basemap', () {
      TransitColors.apply(false);
      final line = sampleConveyance(colorValue: 0xFF000000);

      expect(readableRouteColor(line, isDark: false), const Color(0xFF000000));
    });

    test('keeps a near-white route colour on the dark basemap', () {
      TransitColors.apply(true);
      final line = sampleConveyance(colorValue: 0xFFFFFFFF);

      expect(readableRouteColor(line, isDark: true), const Color(0xFFFFFFFF));
    });
  });

  testWidgets('renders the dark basemap under a dark theme', (tester) async {
    final route = await _withLine(tester);
    final theme = ThemeCubit(store: InMemoryThemeStore(), initial: ThemeMode.dark);
    final vehicleMap = VehicleMapCubit(
      vehicleRepo: FakeVehiclePositionRepo(),
      geometryRepo: FakeRouteGeometryRepo(),
      conveyanceRepo: FakeConveyanceRepo(conveyances: [sampleConveyance()]),
    );
    await tester.runAsync(() => vehicleMap.open(city: sampleCity('Montpellier'), fallbackLine: sampleConveyance()));

    final cubits = TestCubits(
      routeSelection: route,
      vehicleMap: vehicleMap,
      theme: theme,
    );
    addTearDown(cubits.close);
    await pumpApp(tester, Scaffold(body: VehicleMapPage()), cubits: cubits);
    await tester.pump();

    final tiles = tester.widget<TileLayer>(find.byType(TileLayer));
    expect(tiles.urlTemplate, contains('dark_all'));
  });

  testWidgets('shows an idle count badge before any vehicle arrives',
      (tester) async {
    final route = await _withLine(tester);
    final vehicleMap = VehicleMapCubit(
      vehicleRepo: FakeVehiclePositionRepo(),
      geometryRepo: FakeRouteGeometryRepo(),
      conveyanceRepo: FakeConveyanceRepo(conveyances: [sampleConveyance()]),
    );
    await tester.runAsync(() => vehicleMap.open(city: sampleCity('Montpellier'), fallbackLine: sampleConveyance()));

    await _pump(tester, route: route, vehicleMap: vehicleMap);

    expect(find.text('0 véhicules'), findsOneWidget);
  });

  testWidgets('hides the count badge until a line is chosen', (tester) async {
    await _pump(tester);

    expect(find.text('0 véhicules'), findsNothing);
  });

  testWidgets('tapping a stop opens its details sheet with departures',
      (tester) async {
    final route = await _withLine(tester);
    final vehicleMap = VehicleMapCubit(
      vehicleRepo: FakeVehiclePositionRepo(),
      geometryRepo: FakeRouteGeometryRepo(),
      conveyanceRepo: FakeConveyanceRepo(conveyances: [sampleConveyance()]),
    );
    await tester.runAsync(() => vehicleMap.open(city: sampleCity('Montpellier'), fallbackLine: sampleConveyance()));
    final repo = FakeStopDepartureRepo(
      departures: [sampleStopDeparture(headsign: 'Mosson')],
    );
    final departures = StopDeparturesCubit(repo: repo);

    final cubits = TestCubits(
      routeSelection: route,
      vehicleMap: vehicleMap,
      stopDepartures: departures,
    );
    addTearDown(cubits.close);
    await pumpApp(tester, Scaffold(body: VehicleMapPage()), cubits: cubits);
    await tester.pump();

    await tester.tap(find.byKey(const Key('map-stop-s1')), warnIfMissed: false);
    await tester.pump();
    await tester.runAsync(() => Future<void>.delayed(Duration.zero));
    await tester.pump();

    expect(repo.calls, ['s1']);
    expect(find.byType(StopDetailsSheet), findsOneWidget);
  });

  testWidgets('tapping a vehicle opens its details sheet with the headsign',
      (tester) async {
    final route = await _withLine(tester);
    final vehicles = FakeVehiclePositionRepo();
    final vehicleMap = VehicleMapCubit(
      vehicleRepo: vehicles,
      geometryRepo: FakeRouteGeometryRepo(
        geometry: RouteGeometry(
          shapes: const [],
          stops: const [],
          directionHeadsigns: const {0: 'Mosson'},
        ),
      ),
      conveyanceRepo: FakeConveyanceRepo(conveyances: [sampleConveyance()]),
    );
    await tester.runAsync(() => vehicleMap.open(city: sampleCity('Montpellier'), fallbackLine: sampleConveyance()));
    vehicles.controller.add([sampleVehiclePosition(id: 'v1')]);
    await tester.runAsync(() => Future<void>.delayed(Duration.zero));

    final cubits = TestCubits(routeSelection: route, vehicleMap: vehicleMap);
    addTearDown(cubits.close);
    await pumpApp(tester, Scaffold(body: VehicleMapPage()), cubits: cubits);
    await tester.pump();

    await tester.tap(find.byKey(const Key('map-vehicle-v1')), warnIfMissed: false);
    await tester.pump();
    await tester.pump(const Duration(milliseconds: 400));

    expect(find.byType(VehicleDetailsSheet), findsOneWidget);
    expect(find.text('Mosson'), findsOneWidget);
  });

  testWidgets('a stop tap before a city is known still opens the sheet',
      (tester) async {
    final vehicleMap = VehicleMapCubit(
      vehicleRepo: FakeVehiclePositionRepo(),
      geometryRepo: FakeRouteGeometryRepo(),
      conveyanceRepo: FakeConveyanceRepo(conveyances: [sampleConveyance()]),
    );
    final repo = FakeStopDepartureRepo();
    final departures = StopDeparturesCubit(repo: repo);

    final cubits = TestCubits(vehicleMap: vehicleMap, stopDepartures: departures);
    addTearDown(cubits.close);
    await pumpApp(tester, Scaffold(body: VehicleMapPage()), cubits: cubits);
    await tester.pump();

    unawaited(openStopDetails(
      tester.element(find.byType(VehicleMapPage)),
      const RouteStop(id: 's1', name: 'Comédie', latitude: 43.6, longitude: 3.87),
      const Color(0xFF0080C0),
    ));
    await tester.pump();
    await tester.pump(const Duration(milliseconds: 400));

    expect(repo.calls, isEmpty);
    expect(find.byType(StopDetailsSheet), findsOneWidget);
  });

  testWidgets('renders a route whose shape is a single point', (tester) async {
    final route = await _withLine(tester);
    final vehicleMap = VehicleMapCubit(
      vehicleRepo: FakeVehiclePositionRepo(),
      geometryRepo: FakeRouteGeometryRepo(
        geometry: const RouteGeometry(
          shapes: [
            RouteShape(directionId: 0, points: [
              Coordinates(latitude: 43.6, longitude: 3.87),
            ]),
          ],
          stops: [],
        ),
      ),
      conveyanceRepo: FakeConveyanceRepo(conveyances: [sampleConveyance()]),
    );
    await tester.runAsync(() => vehicleMap.open(city: sampleCity('Montpellier'), fallbackLine: sampleConveyance()));

    await _pump(tester, route: route, vehicleMap: vehicleMap);

    expect(find.byType(FlutterMap), findsOneWidget);
    expect(tester.takeException(), isNull);
  });
}
