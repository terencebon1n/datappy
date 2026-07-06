import 'package:frontend/domain/saved_selection.dart' show SavedSelection;


abstract class IFavoritesStore {
    Future<List<SavedSelection>> load();

    Future<void> save(List<SavedSelection> favorites);
}
