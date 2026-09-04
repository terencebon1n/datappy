import 'package:frontend/domain/conveyance.dart' show Conveyance;
import 'package:frontend/domain/route_geometry.dart' show RouteGeometry;
import 'package:frontend/domain/vehicle_position.dart' show VehiclePosition;

enum VehicleMapStatus { idle, loading, live, error }

class VehicleMapState {
    final VehicleMapStatus status;
    final RouteGeometry? geometry;
    final List<VehiclePosition> vehicles;
    final Conveyance? line;
    final List<Conveyance> lines;

    const VehicleMapState({
        this.status = VehicleMapStatus.idle,
        this.geometry,
        this.vehicles = const [],
        this.line,
        this.lines = const [],
    });

    bool get canPickLine => lines.isNotEmpty;

    VehicleMapState copyWith({
        VehicleMapStatus? status,
        RouteGeometry? geometry,
        List<VehiclePosition>? vehicles,
        Conveyance? line,
        List<Conveyance>? lines,
    }) =>
        VehicleMapState(
            status: status ?? this.status,
            geometry: geometry ?? this.geometry,
            vehicles: vehicles ?? this.vehicles,
            line: line ?? this.line,
            lines: lines ?? this.lines,
        );
}
