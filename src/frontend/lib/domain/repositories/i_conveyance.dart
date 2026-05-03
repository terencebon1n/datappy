import 'package:frontend/domain/conveyance.dart' show Conveyance;
import 'package:frontend/domain/route_type.dart' show RouteType;


abstract class IConveyanceRepository {
    Future<List<Conveyance>> resolveConveyances(RouteType routeType);
}
