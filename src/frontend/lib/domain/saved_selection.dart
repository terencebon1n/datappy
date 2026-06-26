import 'package:frontend/domain/city.dart' show City;
import 'package:frontend/domain/conveyance.dart' show Conveyance;
import 'package:frontend/domain/direction.dart' show Direction;


/// A completed transit selection, persisted so it can be restored on the next
/// launch. Bundles everything needed to (a) repaint the dashboard line card and
/// (b) rebuild the websocket path.
class SavedSelection {
    final City city;
    final Conveyance conveyance;
    final String sourceStop;
    final String destStop;
    final Direction direction;

    SavedSelection({
        required this.city,
        required this.conveyance,
        required this.sourceStop,
        required this.destStop,
        required this.direction,
    });
}
