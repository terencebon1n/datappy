import 'package:frontend/domain/city.dart' show City;
import 'package:frontend/domain/route_geometry.dart' show RouteGeometry;


abstract class IRouteGeometryRepository {
    Future<RouteGeometry> resolveRouteGeometry(String routeId, City city);
}
