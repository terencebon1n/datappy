import 'dart:convert' show jsonDecode, jsonEncode;

import 'package:shared_preferences/shared_preferences.dart' show SharedPreferences;

import 'package:frontend/domain/saved_selection.dart' show SavedSelection;
import 'package:frontend/domain/repositories/i_favorites_store.dart' show IFavoritesStore;


/// Persists the favorites as a single JSON array in [SharedPreferences].
class SharedPrefsFavoritesStore implements IFavoritesStore {
    static const String _key = 'favorites';

    final SharedPreferences _prefs;

    SharedPrefsFavoritesStore._(this._prefs);

    /// Loads [SharedPreferences] once so the cubit can read/write synchronously
    /// afterwards.
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
                    favorites.add(
                        SavedSelection.fromJson(entry as Map<String, dynamic>),
                    );
                } catch (_) {
                    // Skip a single corrupt/schema-changed entry, keep the rest.
                }
            }
            return favorites;
        } catch (_) {
            // Corrupt blob: treat as no saved favorites.
            return [];
        }
    }
}
