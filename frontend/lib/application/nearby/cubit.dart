import 'package:flutter_bloc/flutter_bloc.dart';

import 'package:frontend/domain/city.dart' show City;
import 'package:frontend/domain/repositories/i_location.dart'
    show ILocationProvider, LocationPermissionStatus;
import 'package:frontend/domain/repositories/i_nearby_stop.dart'
    show INearbyStopRepository;
import 'state.dart';


class NearbyCubit extends Cubit<NearbyState> {
    final INearbyStopRepository _nearbyRepo;
    final ILocationProvider _location;

    NearbyCubit({
        required INearbyStopRepository nearbyRepo,
        required ILocationProvider location,
    })  : _nearbyRepo = nearbyRepo,
          _location = location,
          super(const NearbyState());

    static const _statusForPermission = {
        LocationPermissionStatus.denied: NearbyStatus.denied,
        LocationPermissionStatus.serviceDisabled: NearbyStatus.serviceDisabled,
    };

    Future<void> findNearby(City city, {int radiusMeters = 800}) async {
        emit(const NearbyState(status: NearbyStatus.locating));

        try {
            final permission = await _location.ensurePermission();
            final refused = _statusForPermission[permission];
            if (refused != null) {
                emit(NearbyState(status: refused));
                return;
            }

            final coordinates = await _location.currentCoordinates();
            emit(const NearbyState(status: NearbyStatus.loading));

            final stops = await _nearbyRepo.resolveNearbyStops(
                coordinates,
                city,
                radiusMeters: radiusMeters,
            );
            emit(NearbyState(status: NearbyStatus.ready, stops: stops));
        } catch (_) {
            emit(const NearbyState(status: NearbyStatus.failed));
        }
    }

    void reset() => emit(const NearbyState());
}
