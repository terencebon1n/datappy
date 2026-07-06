import 'dart:convert' show jsonDecode, jsonEncode;

import 'package:shared_preferences/shared_preferences.dart' show SharedPreferences;

import 'package:frontend/domain/saved_selection.dart' show SavedSelection;
import 'package:frontend/domain/repositories/i_selection_store.dart' show ISelectionStore;


class SharedPrefsSelectionStore implements ISelectionStore {
    static const String _key = 'last_selection';

    final SharedPreferences _prefs;

    SharedPrefsSelectionStore._(this._prefs);

    static Future<SharedPrefsSelectionStore> create() async =>
        SharedPrefsSelectionStore._(await SharedPreferences.getInstance());

    @override
    Future<void> save(SavedSelection s) => _prefs.setString(_key, jsonEncode(s.toJson()));

    @override
    Future<SavedSelection?> load() async {
        final raw = _prefs.getString(_key);
        if (raw == null) return null;
        try {
            return SavedSelection.fromJson(jsonDecode(raw) as Map<String, dynamic>);
        } catch (_) {
            return null;
        }
    }
}
