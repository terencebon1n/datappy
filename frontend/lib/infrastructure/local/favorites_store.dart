import 'dart:convert' show jsonDecode, jsonEncode;

import 'package:shared_preferences/shared_preferences.dart' show SharedPreferences;

import 'package:frontend/domain/saved_selection.dart' show SavedSelection;
import 'package:frontend/domain/repositories/i_favorites_store.dart' show IFavoritesStore;


class SharedPrefsFavoritesStore implements IFavoritesStore {
    static const String _key = 'favorites';

    final SharedPreferences _prefs;

    SharedPrefsFavoritesStore._(this._prefs);

    static Future<SharedPrefsFavoritesStore> create() async =>
        SharedPrefsFavoritesStore._(await SharedPreferences.getInstance());

    @override
    Future<void> save(List<SavedSelection> favorites) =>
        _prefs.setString(_key, jsonEncode([for (final f in favorites) f.toJson()]));

    @override
    Future<List<SavedSelection>> load() async {
        final raw = _prefs.getString(_key);
        if (raw == null) return [];
        try {
            final list = jsonDecode(raw) as List<dynamic>;
            final favorites = <SavedSelection>[];
            for (final entry in list) {
                try {
                    favorites.add(SavedSelection.fromJson(entry as Map<String, dynamic>));
                } catch (_) {
                    continue;
                }
            }
            return favorites;
        } catch (_) {
            return [];
        }
    }
}
