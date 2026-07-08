import 'package:flutter_test/flutter_test.dart';

import 'package:frontend/domain/city.dart';
import 'package:frontend/domain/conveyance.dart';
import 'package:frontend/domain/direction.dart';
import 'package:frontend/domain/saved_selection.dart';

import '../helpers/fakes.dart';

void main() {
  test('toJson / fromJson round-trips every field', () {
    final original = sampleSelection();
    final restored = SavedSelection.fromJson(original.toJson());

    expect(restored.city.name, original.city.name);
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
    expect(
        restored.direction.stopIdDestination, original.direction.stopIdDestination);
  });

  test('equal selections compare equal and share a hashCode', () {
    final a = sampleSelection();
    final b = sampleSelection();
    expect(a, b);
    expect(a.hashCode, b.hashCode);
    expect(a == a, isTrue);
  });

  test('a different type is never equal', () {
    expect(sampleSelection() == Object(), isFalse);
  });

  group('inequality on each identifying field', () {
    final base = sampleSelection();

    SavedSelection withCity(String name) => SavedSelection(
          city: City(name: name),
          conveyance: base.conveyance,
          sourceStop: base.sourceStop,
          destStop: base.destStop,
          direction: base.direction,
        );

    test('city name', () => expect(base == withCity('Paris'), isFalse));

    test('conveyance id', () {
      final other = SavedSelection(
        city: base.city,
        conveyance: Conveyance(
          id: 'B9',
          shortName: base.conveyance.shortName,
          longName: base.conveyance.longName,
          colorValue: base.conveyance.colorValue,
          typeId: base.conveyance.typeId,
          typeName: base.conveyance.typeName,
        ),
        sourceStop: base.sourceStop,
        destStop: base.destStop,
        direction: base.direction,
      );
      expect(base == other, isFalse);
    });

    test('source stop', () {
      final other = SavedSelection(
        city: base.city,
        conveyance: base.conveyance,
        sourceStop: 'Elsewhere',
        destStop: base.destStop,
        direction: base.direction,
      );
      expect(base == other, isFalse);
    });

    test('dest stop', () {
      final other = SavedSelection(
        city: base.city,
        conveyance: base.conveyance,
        sourceStop: base.sourceStop,
        destStop: 'Elsewhere',
        direction: base.direction,
      );
      expect(base == other, isFalse);
    });

    test('direction id', () {
      final other = SavedSelection(
        city: base.city,
        conveyance: base.conveyance,
        sourceStop: base.sourceStop,
        destStop: base.destStop,
        direction: Direction(
          directionId: 1,
          stopIdOrigin: base.direction.stopIdOrigin,
          stopIdDestination: base.direction.stopIdDestination,
        ),
      );
      expect(base == other, isFalse);
    });
  });
}
