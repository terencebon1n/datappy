import 'package:frontend/domain/direction.dart' show Direction;
import 'package:frontend/domain/path.dart' show Path;


abstract class IDirectionRepository {
    abstract Map<String, String> headers;

    Future<Direction> resolveDirection(
        Path path,
    );
}
