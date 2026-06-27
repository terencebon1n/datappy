import 'package:flutter_bloc/flutter_bloc.dart';

import 'package:frontend/domain/repositories/i_favorites_store.dart';
import 'package:frontend/domain/saved_selection.dart';


/// Holds the list of saved favorite selections and persists every change.
/// State is the ordered list itself; [const []] until the store has loaded.
class FavoritesCubit extends Cubit<List<SavedSelection>> {
    final IFavoritesStore _store;

    FavoritesCubit({required IFavoritesStore store})
        : _store = store,
          super(const []) {
        _init();
    }

    Future<void> _init() async => emit(await _store.load());

    /// True when [selection] is already saved (value equality), used to drive
    /// the bookmark icon's filled/outline state.
    bool isFavorite(SavedSelection selection) => state.contains(selection);

    /// Append [selection] unless an equal one is already saved.
    void add(SavedSelection selection) {
        if (state.contains(selection)) return;
        final next = [...state, selection];
        emit(next);
        _store.save(next);
    }

    /// Drop the entry equal to [selection], if present.
    void remove(SavedSelection selection) {
        final next = [
            for (final f in state)
                if (f != selection) f,
        ];
        if (next.length == state.length) return;
        emit(next);
        _store.save(next);
    }

    /// Add when absent, remove when present. Returns true if it is now saved.
    bool toggle(SavedSelection selection) {
        if (isFavorite(selection)) {
            remove(selection);
            return false;
        }
        add(selection);
        return true;
    }
}
