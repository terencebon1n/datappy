import 'package:frontend/domain/saved_selection.dart' show SavedSelection;


abstract class ISelectionStore {
    Future<void> save(SavedSelection selection);

    Future<SavedSelection?> load();
}
