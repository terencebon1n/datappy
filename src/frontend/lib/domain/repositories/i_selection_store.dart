import 'package:frontend/domain/saved_selection.dart' show SavedSelection;


/// Persists the last completed transit selection across app restarts.
abstract class ISelectionStore {
    Future<void> save(SavedSelection selection);

    /// Returns the last saved selection, or null when nothing is saved or the
    /// stored blob can no longer be decoded.
    Future<SavedSelection?> load();
}
