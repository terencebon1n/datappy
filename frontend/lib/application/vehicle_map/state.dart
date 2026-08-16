import 'package:frontend/domain/route_geometry.dart' show RouteGeometry;
import 'package:frontend/domain/vehicle_position.dart' show VehiclePosition;

enum VehicleMapStatus { idle, loading, live, error }

class VehicleMapState {
    final VehicleMapStatus status;
    final RouteGeometry? geometry;
    final List<VehiclePosition> vehicles;

    const VehicleMapState({
        this.status = VehicleMapStatus.idle,
        this.geometry,
        this.vehicles = const [],
    });

    VehicleMapState copyWith({
        VehicleMapStatus? status,
        RouteGeometry? geometry,
        List<VehiclePosition>? vehicles,
    }) =>
        VehicleMapState(
            status: status ?? this.status,
            geometry: geometry ?? this.geometry,
            vehicles: vehicles ?? this.vehicles,
        );
}
