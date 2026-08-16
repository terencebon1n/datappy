import 'package:frontend/domain/nearby_stop.dart' show NearbyStop;

enum NearbyStatus { idle, locating, loading, ready, denied, serviceDisabled, failed }

class NearbyState {
    final NearbyStatus status;
    final List<NearbyStop> stops;

    const NearbyState({
        this.status = NearbyStatus.idle,
        this.stops = const [],
    });

    bool get isBusy =>
        status == NearbyStatus.locating || status == NearbyStatus.loading;
}
