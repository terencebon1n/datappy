import 'dart:async';

import 'package:flutter/material.dart' show ThemeMode;

import 'package:frontend/domain/city.dart';
import 'package:frontend/domain/conveyance.dart';
import 'package:frontend/domain/direction.dart';
import 'package:frontend/domain/path.dart';
import 'package:frontend/domain/coordinates.dart';
import 'package:frontend/domain/nearby_stop.dart';
import 'package:frontend/domain/route_geometry.dart';
import 'package:frontend/domain/vehicle_position.dart';
import 'package:frontend/domain/stop_departure.dart';
import 'package:frontend/domain/stop_update.dart';
import 'package:frontend/domain/alert.dart';
import 'package:frontend/domain/transit_path.dart';
import 'package:frontend/domain/saved_selection.dart';
import 'package:frontend/domain/repositories/i_city.dart';
import 'package:frontend/domain/repositories/i_conveyance.dart';
import 'package:frontend/domain/repositories/i_direction.dart';
import 'package:frontend/domain/repositories/i_stop_name.dart';
import 'package:frontend/domain/repositories/i_location.dart';
import 'package:frontend/domain/repositories/i_nearby_stop.dart';
import 'package:frontend/domain/repositories/i_route_geometry.dart';
import 'package:frontend/domain/repositories/i_vehicle_position.dart';
import 'package:frontend/domain/repositories/i_stop_departure.dart';
import 'package:frontend/domain/repositories/i_stop_update.dart';
import 'package:frontend/domain/repositories/i_alert.dart';
import 'package:frontend/domain/repositories/i_selection_store.dart';
import 'package:frontend/domain/repositories/i_favorites_store.dart';
import 'package:frontend/domain/repositories/i_theme_store.dart';

City sampleCity([String name = 'Lyon']) => City(name: name);

Conveyance sampleConveyance({
  String id = 'T1',
  String shortName = 'T1',
  String longName = 'Tram T1: Perrache - Debourg',
  int colorValue = 0xFF0080C0,
  int typeId = 0,
  String typeName = 'Tramway',
}) =>
    Conveyance(
      id: id,
      shortName: shortName,
      longName: longName,
      colorValue: colorValue,
      typeId: typeId,
      typeName: typeName,
    );

Direction sampleDirection() => Direction(
      directionId: 0,
      stopIdOrigin: 'stop_origin',
      stopIdDestination: 'stop_dest',
    );

TransitPath sampleTransitPath() => TransitPath(
      city: 'lyon',
      routeId: 'T1',
      direction: sampleDirection(),
    );

SavedSelection sampleSelection({String id = 'T1'}) => SavedSelection(
      city: sampleCity(),
      conveyance: sampleConveyance(id: id, shortName: id),
      sourceStop: 'Perrache',
      destStop: 'Debourg',
      direction: sampleDirection(),
    );

StopUpdate sampleStopUpdate({
  String tripId = 'trip-1',
  int? arrivalTime,
  int arrivalDelay = 0,
  int departureTime = 1000,
  int? departureDelay = 0,
  bool isRealtime = true,
}) =>
    StopUpdate(
      tripId: tripId,
      arrivalTime: arrivalTime,
      arrivalDelay: arrivalDelay,
      departureTime: departureTime,
      departureDelay: departureDelay,
      isRealtime: isRealtime,
    );

class FakeCityRepo implements ICityRepository {
  FakeCityRepo({this.cities = const [], this.throwError = false});
  final List<City> cities;
  final bool throwError;

  @override
  Future<List<City>> resolveCities() async {
    if (throwError) throw Exception('boom');
    return cities;
  }
}

class FakeConveyanceRepo implements IConveyanceRepository {
  FakeConveyanceRepo({this.conveyances = const []});
  final List<Conveyance> conveyances;

  @override
  Future<List<Conveyance>> resolveConveyances(City city) async => conveyances;
}

class FakeStopNameRepo implements IStopNameRepository {
  FakeStopNameRepo({this.stops = const []});
  final List<String> stops;

  @override
  Future<List<String>> resolveStopNames(String routeId, City city) async =>
      stops;
}

class FakeDirectionRepo implements IDirectionRepository {
  FakeDirectionRepo({Direction? direction, this.throwError = false, this.gate})
      : direction = direction ?? sampleDirection();
  final Direction direction;
  final bool throwError;
  final Future<void>? gate;
  int calls = 0;

  @override
  Future<Direction> resolveDirection(Path path, City city) async {
    calls++;
    if (gate != null) await gate;
    if (throwError) throw Exception('no direction');
    return direction;
  }
}

class FakeStopUpdateRepo implements IStopUpdateRepository {
  FakeStopUpdateRepo();
  final StreamController<List<StopUpdate>> controller =
      StreamController<List<StopUpdate>>.broadcast();
  final List<TransitPath> calls = [];

  @override
  Stream<List<StopUpdate>> watchStopUpdates(TransitPath transitPath) {
    calls.add(transitPath);
    return controller.stream;
  }
}

class InMemorySelectionStore implements ISelectionStore {
  InMemorySelectionStore([this.selection]);
  SavedSelection? selection;

  @override
  Future<SavedSelection?> load() async => selection;

  @override
  Future<void> save(SavedSelection s) async => selection = s;
}

class InMemoryFavoritesStore implements IFavoritesStore {
  InMemoryFavoritesStore([List<SavedSelection>? initial])
      : saved = initial ?? [];
  List<SavedSelection> saved;

  @override
  Future<List<SavedSelection>> load() async => saved;

  @override
  Future<void> save(List<SavedSelection> favorites) async => saved = favorites;
}

class InMemoryThemeStore implements IThemeStore {
  InMemoryThemeStore([this.mode]);
  ThemeMode? mode;

  @override
  ThemeMode? load() => mode;

  @override
  Future<void> save(ThemeMode m) async => mode = m;
}

Alert sampleAlert({
  String id = 'alert-1',
  String cause = 'STRIKE',
  String effect = 'NO_SERVICE',
  AlertSeverity severity = AlertSeverity.warning,
  String headerText = 'Travaux sur la ligne',
  String descriptionText = 'Circulation interrompue entre A et B.',
  String? url,
}) =>
    Alert(
      id: id,
      cause: cause,
      effect: effect,
      severity: severity,
      headerText: headerText,
      descriptionText: descriptionText,
      url: url,
    );

class FakeAlertRepo implements IAlertRepository {
  FakeAlertRepo({this.alerts = const [], this.throwError = false});
  List<Alert> alerts;
  bool throwError;
  final List<TransitPath> calls = [];

  @override
  Future<List<Alert>> resolveAlerts(TransitPath transitPath) async {
    calls.add(transitPath);
    if (throwError) throw Exception('alert boom');
    return alerts;
  }
}

NearbyStop sampleNearbyStop({
  String name = 'Comédie',
  int distanceMeters = 124,
  double latitude = 43.6085,
  double longitude = 3.8794,
  List<Conveyance>? routes,
}) =>
    NearbyStop(
      name: name,
      distanceMeters: distanceMeters,
      latitude: latitude,
      longitude: longitude,
      routes: routes ?? [sampleConveyance()],
    );

class FakeNearbyStopRepo implements INearbyStopRepository {
  FakeNearbyStopRepo({this.stops = const [], this.throwError = false, this.gate});
  final List<NearbyStop> stops;
  final bool throwError;
  final Future<void>? gate;
  final List<Coordinates> calls = [];
  int? lastRadiusMeters;

  @override
  Future<List<NearbyStop>> resolveNearbyStops(
    Coordinates coordinates,
    City city, {
    int radiusMeters = 800,
  }) async {
    calls.add(coordinates);
    lastRadiusMeters = radiusMeters;
    if (gate != null) await gate;
    if (throwError) throw Exception('nearby boom');
    return stops;
  }
}

class FakeLocationProvider implements ILocationProvider {
  FakeLocationProvider({
    this.permission = LocationPermissionStatus.granted,
    Coordinates? coordinates,
    this.throwError = false,
    this.gate,
  }) : coordinates =
            coordinates ?? const Coordinates(latitude: 43.6085, longitude: 3.8794);
  final LocationPermissionStatus permission;
  final Coordinates coordinates;
  final bool throwError;
  final Future<void>? gate;

  @override
  Future<LocationPermissionStatus> ensurePermission() async => permission;

  @override
  Future<Coordinates> currentCoordinates() async {
    if (gate != null) await gate;
    if (throwError) throw Exception('location boom');
    return coordinates;
  }
}

VehiclePosition sampleVehiclePosition({
  String id = 'v1',
  double latitude = 43.6085,
  double longitude = 3.8794,
  int bearing = 90,
  int directionId = 0,
  int speed = 12,
  String currentStatus = 'IN_TRANSIT_TO',
  int timestamp = 1700000000,
}) =>
    VehiclePosition(
      id: id,
      tripId: 'trip-1',
      routeId: 'T1',
      directionId: directionId,
      latitude: latitude,
      longitude: longitude,
      bearing: bearing,
      speed: speed,
      currentStatus: currentStatus,
      timestamp: timestamp,
    );

RouteGeometry sampleRouteGeometry({
  List<RouteShape>? shapes,
  List<RouteStop>? stops,
}) =>
    RouteGeometry(
      shapes: shapes ??
          const [
            RouteShape(directionId: 0, points: [
              Coordinates(latitude: 43.60, longitude: 3.87),
              Coordinates(latitude: 43.61, longitude: 3.88),
            ]),
          ],
      stops: stops ??
          const [
            RouteStop(
              id: 's1',
              name: 'Comédie',
              latitude: 43.6085,
              longitude: 3.8794,
            ),
          ],
    );

class FakeVehiclePositionRepo implements IVehiclePositionRepository {
  FakeVehiclePositionRepo({this.throwOnSubscribe = false});
  final bool throwOnSubscribe;
  final StreamController<List<VehiclePosition>> controller =
      StreamController<List<VehiclePosition>>.broadcast();
  final List<TransitPath> calls = [];

  @override
  Stream<List<VehiclePosition>> watchVehiclePositions(TransitPath transitPath) {
    calls.add(transitPath);
    if (throwOnSubscribe) throw Exception('socket boom');
    return controller.stream;
  }
}

class FakeRouteGeometryRepo implements IRouteGeometryRepository {
  FakeRouteGeometryRepo({
    RouteGeometry? geometry,
    this.throwError = false,
    this.gate,
  }) : geometry = geometry ?? sampleRouteGeometry();
  final RouteGeometry geometry;
  final bool throwError;
  final Future<void>? gate;
  final List<String> calls = [];

  @override
  Future<RouteGeometry> resolveRouteGeometry(String routeId, City city) async {
    calls.add(routeId);
    if (gate != null) await gate;
    if (throwError) throw Exception('geometry boom');
    return geometry;
  }
}

StopDeparture sampleStopDeparture({
  String tripId = 'trip-1',
  int directionId = 0,
  String headsign = 'Mosson',
  int? departureTime,
  int departureDelay = 0,
  bool isRealtime = true,
}) =>
    StopDeparture(
      tripId: tripId,
      directionId: directionId,
      headsign: headsign,
      departureTime:
          departureTime ?? DateTime.now().millisecondsSinceEpoch ~/ 1000 + 120,
      departureDelay: departureDelay,
      isRealtime: isRealtime,
    );

class FakeStopDepartureRepo implements IStopDepartureRepository {
  FakeStopDepartureRepo({this.departures = const [], this.throwError = false});
  final List<StopDeparture> departures;
  final bool throwError;
  final List<String> calls = [];

  @override
  Future<List<StopDeparture>> resolveStopDepartures({
    required String routeId,
    required String stopId,
    required City city,
  }) async {
    calls.add(stopId);
    if (throwError) throw Exception('departures boom');
    return departures;
  }
}
