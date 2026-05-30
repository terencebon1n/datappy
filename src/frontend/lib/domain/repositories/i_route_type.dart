import 'package:frontend/domain/route_type.dart' show RouteType;


abstract class IRouteTypeRepository {
    abstract Map<String, String> headers;

    Future<List<RouteType>> resolveRouteTypes();
}
