import 'dart:convert' show jsonDecode, jsonEncode;

import 'package:shared_preferences/shared_preferences.dart' show SharedPreferences;

import 'package:frontend/domain/city.dart' show City;
import 'package:frontend/domain/conveyance.dart' show Conveyance;
import 'package:frontend/domain/direction.dart' show Direction;
import 'package:frontend/domain/saved_selection.dart' show SavedSelection;
import 'package:frontend/domain/repositories/i_selection_store.dart' show ISelectionStore;


/// Persists the last selection as a single JSON blob in [SharedPreferences].
class SharedPrefsSelectionStore implements ISelectionStore {
    static const String _key = 'last_selection';

    final SharedPreferences _prefs;

    SharedPrefsSelectionStore._(this._prefs);

    /// Loads [SharedPreferences] once so callers (the cubits) can read/write
    /// synchronously afterwards.
    static Future<SharedPrefsSelectionStore> create() async =>
        SharedPrefsSelectionStore._(await SharedPreferences.getInstance());

    @override
    Future<void> save(SavedSelection s) => _prefs.setString(_key, jsonEncode({
        'city': {'name': s.city.name},
        'conveyance': {
            'id': s.conveyance.id,
            'shortName': s.conveyance.shortName,
            'longName': s.conveyance.longName,
            'colorValue': s.conveyance.colorValue,
            'typeId': s.conveyance.typeId,
            'typeName': s.conveyance.typeName,
        },
        'sourceStop': s.sourceStop,
        'destStop': s.destStop,
        'direction': {
            'directionId': s.direction.directionId,
            'stopIdOrigin': s.direction.stopIdOrigin,
            'stopIdDestination': s.direction.stopIdDestination,
        },
    }));

    @override
    Future<SavedSelection?> load() async {
        final raw = _prefs.getString(_key);
        if (raw == null) return null;
        try {
            final json = jsonDecode(raw) as Map<String, dynamic>;
            final conveyance = json['conveyance'] as Map<String, dynamic>;
            final direction = json['direction'] as Map<String, dynamic>;
            return SavedSelection(
                city: City(name: (json['city'] as Map<String, dynamic>)['name'] as String),
                conveyance: Conveyance(
                    id: conveyance['id'] as String,
                    shortName: conveyance['shortName'] as String,
                    longName: conveyance['longName'] as String,
                    colorValue: conveyance['colorValue'] as int,
                    typeId: conveyance['typeId'] as int,
                    typeName: conveyance['typeName'] as String,
                ),
                sourceStop: json['sourceStop'] as String,
                destStop: json['destStop'] as String,
                direction: Direction(
                    directionId: direction['directionId'] as int,
                    stopIdOrigin: direction['stopIdOrigin'] as String,
                    stopIdDestination: direction['stopIdDestination'] as String,
                ),
            );
        } catch (_) {
            // Corrupt or schema-changed blob: treat as no saved selection.
            return null;
        }
    }
}
