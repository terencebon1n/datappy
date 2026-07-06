import 'package:frontend/domain/direction.dart';

class TransitPath {
    final String city;
    final String routeId;
    final Direction direction;

    TransitPath({
        required this.city,
        required this.routeId,
        required this.direction,
    });
}
