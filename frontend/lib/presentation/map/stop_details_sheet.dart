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

Map<String, List<StopDeparture>> groupByDestination(
  List<StopDeparture> departures,
) {
  final grouped = <String, List<StopDeparture>>{};
  for (final departure in departures) {
    final destination =
        departure.headsign.isEmpty ? 'Direction inconnue' : departure.headsign;
    grouped.putIfAbsent(destination, () => []).add(departure);
  }
  for (final list in grouped.values) {
    list.sort((a, b) => a.departureTime.compareTo(b.departureTime));
  }
  return grouped;
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

    final columns = groupByDestination(state.departures);

    return IntrinsicHeight(
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          for (final entry in columns.entries) ...[
            if (entry.key != columns.keys.first)
              VerticalDivider(
                width: 21,
                thickness: 0.5,
                color: TransitColors.border,
              ),
            Expanded(
              child: _DestinationColumn(
                destination: entry.key,
                departures: entry.value,
                routeColor: routeColor,
                now: now,
              ),
            ),
          ],
        ],
      ),
    );
  }
}

class _DestinationColumn extends StatelessWidget {
  const _DestinationColumn({
    required this.destination,
    required this.departures,
    required this.routeColor,
    required this.now,
  });

  final String destination;
  final List<StopDeparture> departures;
  final Color routeColor;
  final DateTime now;

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          children: [
            Icon(Icons.arrow_right_rounded, size: 16, color: routeColor),
            const SizedBox(width: 2),
            Expanded(
              child: Text(
                destination,
                maxLines: 1,
                overflow: TextOverflow.ellipsis,
                style: TextStyle(
                  fontSize: 12,
                  fontWeight: FontWeight.w700,
                  color: TransitColors.textPrimary,
                ),
              ),
            ),
          ],
        ),
        const SizedBox(height: 6),
        for (final departure in departures)
          _WaitRow(departure: departure, now: now),
      ],
    );
  }
}

class _WaitRow extends StatelessWidget {
  const _WaitRow({required this.departure, required this.now});

  final StopDeparture departure;
  final DateTime now;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        children: [
          _LineBadge(departure: departure),
          const SizedBox(width: 7),
          if (departure.isRealtime) ...[
            Container(
              width: 6,
              height: 6,
              decoration: BoxDecoration(
                shape: BoxShape.circle,
                color: TransitColors.live,
              ),
            ),
            const SizedBox(width: 5),
          ],
          Expanded(
            child: Text(
              formatWait(departure.departureTime, now),
              maxLines: 1,
              overflow: TextOverflow.ellipsis,
              style: TextStyle(
                fontSize: 13,
                fontWeight: FontWeight.w600,
                fontFeatures: const [FontFeature.tabularFigures()],
                color: departure.isRealtime
                    ? TransitColors.live
                    : TransitColors.textSecondary,
              ),
            ),
          ),
        ],
      ),
    );
  }
}

class _LineBadge extends StatelessWidget {
  const _LineBadge({required this.departure});

  final StopDeparture departure;

  @override
  Widget build(BuildContext context) {
    final color = departure.routeColorValue == null
        ? TransitColors.accent
        : Color(departure.routeColorValue!);

    return Container(
      constraints: const BoxConstraints(minWidth: 20),
      padding: const EdgeInsets.symmetric(horizontal: 5, vertical: 2),
      decoration: BoxDecoration(
        color: color.withValues(alpha: 0.14),
        borderRadius: BorderRadius.circular(5),
        border: Border.all(color: color.withValues(alpha: 0.45)),
      ),
      child: Text(
        departure.routeShortName.isEmpty ? '?' : departure.routeShortName,
        textAlign: TextAlign.center,
        maxLines: 1,
        overflow: TextOverflow.ellipsis,
        style: TextStyle(
          fontSize: 10,
          fontWeight: FontWeight.w700,
          color: TransitColors.textPrimary,
        ),
      ),
    );
  }
}
