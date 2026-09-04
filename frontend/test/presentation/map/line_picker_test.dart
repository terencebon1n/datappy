import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

import 'package:frontend/application/vehicle_map/cubit.dart';
import 'package:frontend/presentation/funnel/funnel_widgets.dart';
import 'package:frontend/presentation/map/line_picker_sheet.dart';
import 'package:frontend/presentation/map/vehicle_map_page.dart';

import '../../helpers/fakes.dart';
import '../../helpers/pump.dart';

final _tram1 = sampleConveyance(id: 'T1', shortName: '1', typeName: 'Tram', typeId: 0);
final _tram4 = sampleConveyance(id: 'T4', shortName: '4', typeName: 'Tram', typeId: 0);
final _bus9 = sampleConveyance(id: 'B9', shortName: '9', typeName: 'Bus', typeId: 3);

Future<VehicleMapCubit> _pumpMap(
  WidgetTester tester, {
  List? lines,
  bool selectLine = true,
}) async {
  final cubit = VehicleMapCubit(
    vehicleRepo: FakeVehiclePositionRepo(),
    geometryRepo: FakeRouteGeometryRepo(),
    conveyanceRepo:
        FakeConveyanceRepo(conveyances: (lines ?? [_tram1, _tram4, _bus9]).cast()),
  );
  await tester.runAsync(() => cubit.open(
        city: sampleCity('Montpellier'),
        fallbackLine: selectLine ? _tram1 : null,
      ));

  final cubits = TestCubits(vehicleMap: cubit);
  addTearDown(cubits.close);
  await pumpApp(tester, Scaffold(body: VehicleMapPage()), cubits: cubits);
  await tester.pump();
  return cubit;
}

void main() {
  group('groupLinesByType', () {
    test('groups lines under their type name', () {
      final groups = groupLinesByType([_tram1, _bus9, _tram4]);

      expect(groups.keys, ['Tram', 'Bus']);
      expect(groups['Tram'], hasLength(2));
      expect(groups['Bus'], hasLength(1));
    });

    test('yields nothing for no lines', () {
      expect(groupLinesByType([]), isEmpty);
    });
  });

  testWidgets('the header names the selected line', (tester) async {
    await _pumpMap(tester);

    expect(find.text('Ligne 1'), findsOneWidget);
  });

  testWidgets('the header invites a pick when no line is selected',
      (tester) async {
    await _pumpMap(tester, selectLine: false);

    expect(find.text('Choisir une ligne'), findsWidgets);
  });

  testWidgets('tapping the header opens the picker', (tester) async {
    await _pumpMap(tester);

    await tester.tap(find.text('Ligne 1'));
    await tester.pump();
    await tester.pump(const Duration(milliseconds: 400));

    expect(find.byType(LinePickerSheet), findsOneWidget);
    expect(find.text('TRAM'), findsOneWidget);
    expect(find.text('BUS'), findsOneWidget);
  });

  testWidgets('picking a line switches the map to it', (tester) async {
    final cubit = await _pumpMap(tester);

    await tester.tap(find.text('Ligne 1'));
    await tester.pump();
    await tester.pump(const Duration(milliseconds: 400));

    await tester.tap(find.byType(RouteListTile).at(2));
    await tester.pump();
    await tester.runAsync(() => Future<void>.delayed(Duration.zero));
    await tester.pump(const Duration(milliseconds: 400));

    expect(cubit.state.line?.id, 'B9');
    expect(find.byType(LinePickerSheet), findsNothing);
  });

  testWidgets('the empty state offers the picker', (tester) async {
    await _pumpMap(tester, selectLine: false);

    await tester.tap(find.widgetWithText(TextButton, 'Choisir une ligne'));
    await tester.pump();
    await tester.pump(const Duration(milliseconds: 400));

    expect(find.byType(LinePickerSheet), findsOneWidget);
  });

  testWidgets('the header is inert when no lines could be loaded',
      (tester) async {
    await _pumpMap(tester, lines: const [], selectLine: false);

    expect(find.byIcon(Icons.unfold_more_rounded), findsNothing);
    expect(find.widgetWithText(TextButton, 'Choisir une ligne'), findsNothing);
  });

  testWidgets('the picker reports when no lines are available', (tester) async {
    final cubit = VehicleMapCubit(
      vehicleRepo: FakeVehiclePositionRepo(),
      geometryRepo: FakeRouteGeometryRepo(),
      conveyanceRepo: FakeConveyanceRepo(),
    );
    final cubits = TestCubits(vehicleMap: cubit);
    addTearDown(cubits.close);

    await pumpApp(
      tester,
      Scaffold(body: LinePickerSheet(onSelected: (_) {})),
      cubits: cubits,
    );
    await tester.pump();

    expect(find.text('Aucune ligne disponible.'), findsOneWidget);
    expect(find.byType(RouteListTile), findsNothing);
  });
}
