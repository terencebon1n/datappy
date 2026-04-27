import 'package:frontend/domain/direction.dart';

abstract class IDirectionRepository {
  Future<Direction> resolveDirection({
    required String routeId,
    required String originName,
    required String destinationName,
  });
}
