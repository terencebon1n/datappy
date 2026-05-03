import 'package:frontend/domain/direction.dart' show Direction;
import 'package:frontend/domain/path.dart' show Path;


abstract class IDirectionRepository {
    Future<Direction> resolveDirection(
        Path path,
    );
}
