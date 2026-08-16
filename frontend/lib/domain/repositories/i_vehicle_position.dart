import 'package:frontend/domain/transit_path.dart' show TransitPath;
import 'package:frontend/domain/vehicle_position.dart' show VehiclePosition;


abstract class IVehiclePositionRepository {
    Stream<List<VehiclePosition>> watchVehiclePositions(TransitPath transitPath);
}
