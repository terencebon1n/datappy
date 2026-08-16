import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';

import 'package:frontend/application/stop_departures/cubit.dart';
import 'package:frontend/application/stop_departures/state.dart';
import 'package:frontend/domain/route_geometry.dart';
import 'package:frontend/domain/stop_departure.dart';
import 'package:frontend/presentation/map/sheet_widgets.dart';
import 'package:frontend/presentation/theme/colors.dart';

String formatWait(int departureTime, DateTime now) {
  final seconds = departureTime - now.millisecondsSinceEpoch ~/ 1000;
  if (seconds <= 30) return "à l'approche";
  final minutes = (seconds / 60).round();
  if (minutes < 60) return '$minutes min';
  final hours = minutes ~/ 60;
  return '$hours h ${(minutes % 60).toString().padLeft(2, '0')}';
}

class StopDetailsSheet extends StatelessWidget {
  const StopDetailsSheet({
    super.key,
    required this.stop,
    required this.routeColor,
    required this.now,
  });

  final RouteStop stop;
  final Color routeColor;
  final DateTime now;

  @override
  Widget build(BuildContext context) {
    final state = context.watch<StopDeparturesCubit>().state;

    return SheetShell(
      children: [
        SheetTitle(
          icon: Icons.place_rounded,
          iconColor: routeColor,
          title: stop.name,
          trailing: stop.platformCode == null
              ? null
              : SheetChip(label: 'Quai ${stop.platformCode}'),
        ),
        const SizedBox(height: 10),
        Wrap(
          spacing: 8,
          runSpacing: 8,
          children: [
            if (stop.code != null) SheetChip(label: 'Code ${stop.code}'),
            if (stop.isWheelchairAccessible)
              const SheetChip(
                label: 'Accessible',
                icon: Icons.accessible_rounded,
              ),
            if (stop.isWheelchairInaccessible)
              const SheetChip(
                label: 'Non accessible',
                icon: Icons.not_accessible_rounded,
              ),
          ],
        ),
        const SizedBox(height: 16),
        SheetSectionLabel('Prochains départs'),
        const SizedBox(height: 8),
        _Departures(state: state, routeColor: routeColor, now: now),
      ],
    );
  }
}

class _Departures extends StatelessWidget {
  const _Departures({
    required this.state,
    required this.routeColor,
    required this.now,
  });

  final StopDeparturesState state;
  final Color routeColor;
  final DateTime now;

  @override
  Widget build(BuildContext context) {
    if (state.status == StopDeparturesStatus.loading) {
      return Padding(
        padding: const EdgeInsets.symmetric(vertical: 18),
        child: Center(
          child: SizedBox(
            width: 20,
            height: 20,
            child: CircularProgressIndicator(
              strokeWidth: 2,
              color: TransitColors.accent,
            ),
          ),
        ),
      );
    }

    if (state.status == StopDeparturesStatus.error) {
      return SheetEmpty(text: 'Départs indisponibles.');
    }

    if (state.departures.isEmpty) {
      return SheetEmpty(text: 'Aucun départ prévu.');
    }

    return Column(
      children: [
        for (final departure in state.departures)
          _DepartureRow(
            departure: departure,
            routeColor: routeColor,
            now: now,
          ),
      ],
    );
  }
}

class _DepartureRow extends StatelessWidget {
  const _DepartureRow({
    required this.departure,
    required this.routeColor,
    required this.now,
  });

  final StopDeparture departure;
  final Color routeColor;
  final DateTime now;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 7),
      child: Row(
        children: [
          Icon(Icons.arrow_right_rounded, size: 18, color: routeColor),
          const SizedBox(width: 6),
          Expanded(
            child: Text(
              departure.headsign.isEmpty ? 'Direction inconnue' : departure.headsign,
              maxLines: 1,
              overflow: TextOverflow.ellipsis,
              style: TextStyle(
                fontSize: 13,
                fontWeight: FontWeight.w500,
                color: TransitColors.textPrimary,
              ),
            ),
          ),
          if (departure.isRealtime) ...[
            Container(
              width: 6,
              height: 6,
              decoration: BoxDecoration(
                shape: BoxShape.circle,
                color: TransitColors.live,
              ),
            ),
            const SizedBox(width: 6),
          ],
          Text(
            formatWait(departure.departureTime, now),
            style: TextStyle(
              fontSize: 13,
              fontWeight: FontWeight.w600,
              fontFeatures: const [FontFeature.tabularFigures()],
              color: departure.isRealtime
                  ? TransitColors.live
                  : TransitColors.textSecondary,
            ),
          ),
        ],
      ),
    );
  }
}
