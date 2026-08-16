import 'package:flutter_test/flutter_test.dart';
import 'package:geolocator/geolocator.dart';

import 'package:frontend/domain/repositories/i_location.dart';
import 'package:frontend/infrastructure/device/location.dart';

class _FakeGeolocatorPlatform extends GeolocatorPlatform {
  _FakeGeolocatorPlatform({
    this.serviceEnabled = true,
    this.permission = LocationPermission.always,
    this.permissionAfterRequest = LocationPermission.always,
  });

  final bool serviceEnabled;
  final LocationPermission permission;
  final LocationPermission permissionAfterRequest;

  int requestCount = 0;

  @override
  Future<bool> isLocationServiceEnabled() async => serviceEnabled;

  @override
  Future<LocationPermission> checkPermission() async => permission;

  @override
  Future<LocationPermission> requestPermission() async {
    requestCount++;
    return permissionAfterRequest;
  }

  @override
  Future<Position> getCurrentPosition({LocationSettings? locationSettings}) async =>
      Position(
        latitude: 43.6085,
        longitude: 3.8794,
        timestamp: DateTime.utc(2026),
        accuracy: 5,
        altitude: 0,
        altitudeAccuracy: 0,
        heading: 0,
        headingAccuracy: 0,
        speed: 0,
        speedAccuracy: 0,
      );
}

void main() {
  late GeolocatorLocationProvider provider;

  setUp(() => provider = GeolocatorLocationProvider());

  test('reports a disabled location service', () async {
    GeolocatorPlatform.instance =
        _FakeGeolocatorPlatform(serviceEnabled: false);

    expect(
      await provider.ensurePermission(),
      LocationPermissionStatus.serviceDisabled,
    );
  });

  test('grants when permission is already held', () async {
    final platform = _FakeGeolocatorPlatform(
      permission: LocationPermission.whileInUse,
    );
    GeolocatorPlatform.instance = platform;

    expect(
      await provider.ensurePermission(),
      LocationPermissionStatus.granted,
    );
    expect(platform.requestCount, 0);
  });

  test('requests permission when it has not been asked yet', () async {
    final platform = _FakeGeolocatorPlatform(
      permission: LocationPermission.denied,
      permissionAfterRequest: LocationPermission.whileInUse,
    );
    GeolocatorPlatform.instance = platform;

    expect(
      await provider.ensurePermission(),
      LocationPermissionStatus.granted,
    );
    expect(platform.requestCount, 1);
  });

  test('denies when the request is refused', () async {
    GeolocatorPlatform.instance = _FakeGeolocatorPlatform(
      permission: LocationPermission.denied,
      permissionAfterRequest: LocationPermission.denied,
    );

    expect(
      await provider.ensurePermission(),
      LocationPermissionStatus.denied,
    );
  });

  test('denies when permission was refused for good', () async {
    GeolocatorPlatform.instance = _FakeGeolocatorPlatform(
      permission: LocationPermission.deniedForever,
    );

    expect(
      await provider.ensurePermission(),
      LocationPermissionStatus.denied,
    );
  });

  test('maps the current position onto domain coordinates', () async {
    GeolocatorPlatform.instance = _FakeGeolocatorPlatform();

    final coordinates = await provider.currentCoordinates();

    expect(coordinates.latitude, 43.6085);
    expect(coordinates.longitude, 3.8794);
  });
}
