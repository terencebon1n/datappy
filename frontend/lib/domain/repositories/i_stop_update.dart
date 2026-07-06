import 'package:frontend/domain/stop_update.dart' show StopUpdate;
import 'package:frontend/domain/transit_path.dart' show TransitPath;


abstract class IStopUpdateRepository {
    Stream<List<StopUpdate>> watchStopUpdates(
        TransitPath transitPath
    );
}
