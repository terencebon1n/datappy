import 'package:flutter_test/flutter_test.dart';
import 'package:shared_preferences/shared_preferences.dart';

import 'package:frontend/domain/city.dart';
import 'package:frontend/domain/conveyance.dart';
import 'package:frontend/domain/direction.dart';
import 'package:frontend/domain/saved_selection.dart';
import 'package:frontend/infrastructure/local/selection_store.dart';

SavedSelection _sample() => SavedSelection(
      city: City(name: 'Lyon'),
      conveyance: Conveyance(
        id: 'T1',
        shortName: 'T1',
        longName: 'Tram T1: Perrache - Debourg',
        colorValue: 0xFF0080C0,
        typeId: 0,
        typeName: 'Tramway',
      ),
      sourceStop: 'Perrache',
      destStop: 'Debourg',
      direction: Direction(
        directionId: 0,
        stopIdOrigin: 'stop_origin',
        stopIdDestination: 'stop_dest',
      ),
    );

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  test('load returns null when nothing has been saved', () async {
    SharedPreferences.setMockInitialValues({});
    final store = await SharedPrefsSelectionStore.create();
    expect(await store.load(), isNull);
  });

  test('save then load round-trips every field', () async {
    SharedPreferences.setMockInitialValues({});
    final store = await SharedPrefsSelectionStore.create();
    final original = _sample();

    await store.save(original);
    final restored = await store.load();

    expect(restored, isNotNull);
    expect(restored!.city.name, original.city.name);
    expect(restored.conveyance.id, original.conveyance.id);
    expect(restored.conveyance.shortName, original.conveyance.shortName);
    expect(restored.conveyance.longName, original.conveyance.longName);
    expect(restored.conveyance.colorValue, original.conveyance.colorValue);
    expect(restored.conveyance.typeId, original.conveyance.typeId);
    expect(restored.conveyance.typeName, original.conveyance.typeName);
    expect(restored.sourceStop, original.sourceStop);
    expect(restored.destStop, original.destStop);
    expect(restored.direction.directionId, original.direction.directionId);
    expect(restored.direction.stopIdOrigin, original.direction.stopIdOrigin);
    expect(restored.direction.stopIdDestination, original.direction.stopIdDestination);
  });

  test('load returns null for a corrupt blob', () async {
    SharedPreferences.setMockInitialValues({'last_selection': 'not json {'});
    final store = await SharedPrefsSelectionStore.create();
    expect(await store.load(), isNull);
  });
}
