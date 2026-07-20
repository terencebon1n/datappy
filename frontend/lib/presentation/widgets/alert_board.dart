import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';

import 'package:frontend/application/alert/cubit.dart';
import 'package:frontend/application/alert/state.dart';
import 'package:frontend/domain/alert.dart';
import 'package:frontend/presentation/theme/colors.dart';

class AlertBoard extends StatelessWidget {
  const AlertBoard({super.key});

  @override
  Widget build(BuildContext context) {
    final state = context.watch<AlertCubit>().state;
    if (state is! AlertLoaded || state.alerts.isEmpty) {
      return const SizedBox.shrink();
    }

    return Padding(
      padding: const EdgeInsets.only(top: 10),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          _header(state.alerts.length),
          const SizedBox(height: 6),
          for (final alert in state.alerts) _AlertCard(alert: alert),
        ],
      ),
    );
  }

  static Widget _header(int count) {
    return Padding(
      padding: const EdgeInsets.only(left: 2, bottom: 2),
      child: Text(
        count > 1 ? '$count informations trafic' : 'Information trafic',
        style: TextStyle(
          fontSize: 9,
          fontWeight: FontWeight.w600,
          letterSpacing: 0.6,
          color: TransitColors.textMuted,
        ),
      ),
    );
  }
}

class _AlertCard extends StatelessWidget {
  const _AlertCard({required this.alert});

  final Alert alert;

  @override
  Widget build(BuildContext context) {
    final color = severityColor(alert.severity);

    return Container(
      margin: const EdgeInsets.only(bottom: 6),
      decoration: BoxDecoration(
        color: TransitColors.surface,
        borderRadius: BorderRadius.circular(10),
        border: Border.all(color: TransitColors.border),
      ),
      child: IntrinsicHeight(
        child: Row(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Container(
              width: 3,
              decoration: BoxDecoration(
                color: color,
                borderRadius: const BorderRadius.horizontal(
                  left: Radius.circular(10),
                ),
              ),
            ),
            Expanded(
              child: Padding(
                padding: const EdgeInsets.fromLTRB(10, 9, 10, 9),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        Icon(severityIcon(alert.severity), size: 12, color: color),
                        const SizedBox(width: 5),
                        Expanded(
                          child: Text(
                            alert.headerText,
                            style: TextStyle(
                              fontSize: 11.5,
                              fontWeight: FontWeight.w600,
                              color: TransitColors.textPrimary,
                            ),
                          ),
                        ),
                      ],
                    ),
                    if (alert.descriptionText.isNotEmpty) ...[
                      const SizedBox(height: 4),
                      Text(
                        alert.descriptionText,
                        style: TextStyle(
                          fontSize: 10.5,
                          height: 1.35,
                          color: TransitColors.textSecondary,
                        ),
                      ),
                    ],
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

Color severityColor(AlertSeverity severity) => switch (severity) {
  AlertSeverity.severe  => TransitColors.bad,
  AlertSeverity.warning => TransitColors.warn,
  AlertSeverity.info    => TransitColors.accent,
  AlertSeverity.unknown => TransitColors.textSecondary,
};

IconData severityIcon(AlertSeverity severity) => switch (severity) {
  AlertSeverity.severe  => Icons.error_outline,
  AlertSeverity.warning => Icons.warning_amber_outlined,
  AlertSeverity.info    => Icons.info_outline,
  AlertSeverity.unknown => Icons.campaign_outlined,
};
