import 'package:flutter_bloc/flutter_bloc.dart';

import 'package:frontend/domain/repositories/i_favorites_store.dart';
import 'package:frontend/domain/saved_selection.dart';


class FavoritesCubit extends Cubit<List<SavedSelection>> {
    final IFavoritesStore _store;

    FavoritesCubit({required IFavoritesStore store})
        : _store = store,
          super(const []) {
        _init();
    }

    Future<void> _init() async => emit(await _store.load());

    bool isFavorite(SavedSelection selection) => state.contains(selection);

    void add(SavedSelection selection) {
        if (state.contains(selection)) return;
        final next = [...state, selection];
        emit(next);
        _store.save(next);
    }

    void remove(SavedSelection selection) {
        final next = [
            for (final f in state)
                if (f != selection) f,
        ];
        if (next.length == state.length) return;
        emit(next);
        _store.save(next);
    }

    bool toggle(SavedSelection selection) {
        if (isFavorite(selection)) {
            remove(selection);
            return false;
        }
        add(selection);
        return true;
    }
}
