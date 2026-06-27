import 'package:frontend/domain/saved_selection.dart' show SavedSelection;


/// Persists the user's saved favorite selections across app restarts.
abstract class IFavoritesStore {
    /// Returns the saved favorites in order, or an empty list when nothing is
    /// saved or the stored blob can no longer be decoded.
    Future<List<SavedSelection>> load();

    Future<void> save(List<SavedSelection> favorites);
}
