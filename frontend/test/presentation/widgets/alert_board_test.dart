import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

import 'package:frontend/application/alert/cubit.dart';
import 'package:frontend/domain/alert.dart';
import 'package:frontend/presentation/theme/colors.dart';
import 'package:frontend/presentation/widgets/alert_board.dart';

import '../../helpers/fakes.dart';
import '../../helpers/pump.dart';

Future<TestCubits> _pumpBoard(
  WidgetTester tester,
  List<Alert> alerts, {
  bool watch = true,
}) async {
  final cubit = AlertCubit(
    alertRepo: FakeAlertRepo(alerts: alerts),
    selectionStore: InMemorySelectionStore(),
  );
  final cubits = TestCubits(alert: cubit);
  await pumpApp(tester, const Scaffold(body: AlertBoard()), cubits: cubits);
  if (watch) {
    await cubit.watchAlerts(sampleTransitPath());
    await tester.pump();
  }
  return cubits;
}

void main() {
  testWidgets('renders nothing while idle', (tester) async {
    final cubits = await _pumpBoard(tester, [], watch: false);

    expect(find.byType(Text), findsNothing);

    cubits.alert.stop();
    await tester.pumpWidget(const SizedBox());
  });

  testWidgets('renders nothing when there is no alert', (tester) async {
    final cubits = await _pumpBoard(tester, []);

    expect(find.byType(Text), findsNothing);

    cubits.alert.stop();
    await tester.pumpWidget(const SizedBox());
  });

  testWidgets('renders nothing when the fetch failed', (tester) async {
    final cubit = AlertCubit(
      alertRepo: FakeAlertRepo(throwError: true),
      selectionStore: InMemorySelectionStore(),
    );
    final cubits = TestCubits(alert: cubit);
    await pumpApp(tester, const Scaffold(body: AlertBoard()), cubits: cubits);
    await cubit.watchAlerts(sampleTransitPath());
    await tester.pump();

    expect(find.byType(Text), findsNothing);

    cubits.alert.stop();
    await tester.pumpWidget(const SizedBox());
  });

  testWidgets('shows a single alert with its header and description',
      (tester) async {
    final cubits = await _pumpBoard(tester, [sampleAlert()]);

    expect(find.text('Information trafic'), findsOneWidget);
    expect(find.text('Travaux sur la ligne'), findsOneWidget);
    expect(find.text('Circulation interrompue entre A et B.'), findsOneWidget);

    cubits.alert.stop();
    await tester.pumpWidget(const SizedBox());
  });

  testWidgets('pluralises the header for several alerts', (tester) async {
    final cubits = await _pumpBoard(tester, [
      sampleAlert(),
      sampleAlert(id: 'a2', headerText: 'Retards'),
    ]);

    expect(find.text('2 informations trafic'), findsOneWidget);
    expect(find.text('Retards'), findsOneWidget);

    cubits.alert.stop();
    await tester.pumpWidget(const SizedBox());
  });

  testWidgets('omits the description when it is empty', (tester) async {
    final cubits = await _pumpBoard(tester, [
      sampleAlert(descriptionText: ''),
    ]);

    expect(find.text('Travaux sur la ligne'), findsOneWidget);
    expect(find.byType(Text), findsNWidgets(2)); // header label + alert title

    cubits.alert.stop();
    await tester.pumpWidget(const SizedBox());
  });

  testWidgets('each severity gets its own colour and icon', (tester) async {
    final cubits = await _pumpBoard(tester, [
      sampleAlert(id: 'a1', severity: AlertSeverity.severe),
      sampleAlert(id: 'a2', severity: AlertSeverity.warning),
      sampleAlert(id: 'a3', severity: AlertSeverity.info),
      sampleAlert(id: 'a4', severity: AlertSeverity.unknown),
    ]);

    expect(find.byIcon(Icons.error_outline), findsOneWidget);
    expect(find.byIcon(Icons.warning_amber_outlined), findsOneWidget);
    expect(find.byIcon(Icons.info_outline), findsOneWidget);
    expect(find.byIcon(Icons.campaign_outlined), findsOneWidget);

    cubits.alert.stop();
    await tester.pumpWidget(const SizedBox());
  });

  test('severity maps to the palette', () {
    TransitColors.apply(false);
    expect(severityColor(AlertSeverity.severe), TransitColors.bad);
    expect(severityColor(AlertSeverity.warning), TransitColors.warn);
    expect(severityColor(AlertSeverity.info), TransitColors.accent);
    expect(severityColor(AlertSeverity.unknown), TransitColors.textSecondary);
  });
}
