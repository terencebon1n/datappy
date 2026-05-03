import 'package:frontend/domain/path.dart' show Path;


abstract class IPathRepository {
    Future<Path> resolvePath({
        required String routeId,
        required String originName,
        required String destinationName,
    });
}
