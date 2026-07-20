import 'package:frontend/domain/alert.dart' show Alert;
import 'package:frontend/domain/transit_path.dart' show TransitPath;


abstract class IAlertRepository {
    Future<List<Alert>> resolveAlerts(
        TransitPath transitPath
    );
}
