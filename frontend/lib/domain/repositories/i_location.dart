import 'package:frontend/domain/coordinates.dart' show Coordinates;


enum LocationPermissionStatus { granted, denied, serviceDisabled }

abstract class ILocationProvider {
    Future<LocationPermissionStatus> ensurePermission();

    Future<Coordinates> currentCoordinates();
}
