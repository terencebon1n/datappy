import 'package:frontend/domain/stop_update.dart';

abstract class IStopUpdateRepository {
    Stream<List<StopUpdate>> watchStopUpdates(
        String city,
        String routeId,
        int directionId,
        String stopIdOrigin,
        String stopIdDestination,
    );
}
