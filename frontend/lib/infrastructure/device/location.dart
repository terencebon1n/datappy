import 'package:geolocator/geolocator.dart';

import 'package:frontend/domain/coordinates.dart' show Coordinates;
import 'package:frontend/domain/repositories/i_location.dart'
    show ILocationProvider, LocationPermissionStatus;


class GeolocatorLocationProvider implements ILocationProvider {
    @override
    Future<LocationPermissionStatus> ensurePermission() async {
        if (!await Geolocator.isLocationServiceEnabled()) {
            return LocationPermissionStatus.serviceDisabled;
        }

        var permission = await Geolocator.checkPermission();
        if (permission == LocationPermission.denied) {
            permission = await Geolocator.requestPermission();
        }

        if (permission == LocationPermission.denied ||
            permission == LocationPermission.deniedForever) {
            return LocationPermissionStatus.denied;
        }

        return LocationPermissionStatus.granted;
    }

    @override
    Future<Coordinates> currentCoordinates() async {
        final position = await Geolocator.getCurrentPosition(
            locationSettings: const LocationSettings(accuracy: LocationAccuracy.medium),
        );

        return Coordinates(
            latitude: position.latitude,
            longitude: position.longitude,
        );
    }
}
