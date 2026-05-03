import 'package:frontend/domain/route_type.dart' show RouteType;


abstract class IRouteTypeRepository {
    Future<List<RouteType>> resolveRouteTypes();
}
