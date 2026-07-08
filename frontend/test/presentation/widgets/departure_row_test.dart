import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

import 'package:frontend/presentation/theme/colors.dart';
import 'package:frontend/presentation/widgets/departure_row.dart';

class _Dep {
  _Dep({this.departureTime, this.arrivalDelay, required this.isRealtime});
  final int? departureTime;
  final int? arrivalDelay;
  final bool isRealtime;
}

const _nowSec = 1700000000;
final _now = DateTime.fromMillisecondsSinceEpoch(_nowSec * 1000);

Future<void> _pump(
  WidgetTester tester,
  Object departure, {
  bool showDivider = false,
}) {
  TransitColors.apply(false);
  return tester.pumpWidget(
    MaterialApp(
      home: Scaffold(
        body: DepartureRow(
          rank: 1,
          departure: departure,
          now: _now,
          opacity: 1,
          showDivider: showDivider,
        ),
      ),
    ),
  );
}

void main() {
  testWidgets('null departure time shows placeholders', (tester) async {
    await _pump(tester, _Dep(departureTime: null, arrivalDelay: null, isRealtime: true));
    expect(find.text('--:--'), findsOneWidget);
    expect(find.textContaining('--:--'), findsWidgets);
  });

  testWidgets('a departure in the past reads "À quai"', (tester) async {
    await _pump(tester, _Dep(departureTime: _nowSec - 10, arrivalDelay: 0, isRealtime: true));
    expect(find.text('À quai'), findsOneWidget);
  });

  testWidgets('under a minute counts in seconds', (tester) async {
    await _pump(tester, _Dep(departureTime: _nowSec + 30, arrivalDelay: 0, isRealtime: true));
    expect(find.text('30 s'), findsOneWidget);
  });

  testWidgets('over a minute counts in minutes and seconds', (tester) async {
    await _pump(tester, _Dep(departureTime: _nowSec + 130, arrivalDelay: 0, isRealtime: true));
    expect(find.text('2 min 10 s'), findsOneWidget);
    expect(find.textContaining('Départ prévue'), findsOneWidget);
  });

  testWidgets('realtime uses the sensors icon; scheduled uses the clock', (tester) async {
    await _pump(tester, _Dep(departureTime: _nowSec + 30, arrivalDelay: 0, isRealtime: true));
    expect(find.byIcon(Icons.sensors), findsOneWidget);

    await _pump(tester, _Dep(departureTime: _nowSec + 30, arrivalDelay: 0, isRealtime: false),
        showDivider: true);
    expect(find.byIcon(Icons.schedule), findsOneWidget);
    expect(find.byType(Divider), findsOneWidget);
  });
}
