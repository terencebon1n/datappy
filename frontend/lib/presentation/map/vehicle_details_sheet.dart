import 'package:flutter/material.dart';

import 'package:frontend/domain/vehicle_position.dart';
import 'package:frontend/presentation/map/sheet_widgets.dart';
import 'package:frontend/presentation/theme/colors.dart';

const _statusLabels = {
  'IN_TRANSIT_TO': 'En circulation',
  'INCOMING_AT': "À l'approche",
  'STOPPED_AT': "À l'arrêt",
};

const _compassPoints = [
  'Nord',
  'Nord-Est',
  'Est',
  'Sud-Est',
  'Sud',
  'Sud-Ouest',
  'Ouest',
  'Nord-Ouest',
];

String vehicleStatusLabel(String status) =>
    _statusLabels[status] ?? 'Position connue';

String compassLabel(int bearing) {
  final normalized = ((bearing % 360) + 360) % 360;
  return _compassPoints[(((normalized + 22.5) % 360) ~/ 45)];
}

String formatSpeed(int metresPerSecond) =>
    '${(metresPerSecond * 3.6).round()} km/h';

String formatAge(int timestamp, DateTime now) {
  final seconds = now.millisecondsSinceEpoch ~/ 1000 - timestamp;
  if (seconds < 0) return "à l'instant";
  if (seconds < 60) return 'il y a $seconds s';
  final minutes = seconds ~/ 60;
  if (minutes < 60) return 'il y a $minutes min';
  return 'il y a ${minutes ~/ 60} h';
}

class VehicleDetailsSheet extends StatelessWidget {
  const VehicleDetailsSheet({
    super.key,
    required this.vehicle,
    required this.routeColor,
    required this.headsign,
    required this.now,
  });

  final VehiclePosition vehicle;
  final Color routeColor;
  final String? headsign;
  final DateTime now;

  @override
  Widget build(BuildContext context) {
    final live = vehicle.currentStatus != 'STOPPED_AT';

    return SheetShell(
      children: [
        SheetTitle(
          icon: Icons.directions_transit_rounded,
          iconColor: routeColor,
          title: headsign == null || headsign!.isEmpty
              ? 'Véhicule ${vehicle.id}'
              : headsign!,
          subtitle: 'Véhicule ${vehicle.id}',
          trailing: SheetChip(
            label: vehicleStatusLabel(vehicle.currentStatus),
            icon: live ? Icons.play_arrow_rounded : Icons.pause_rounded,
          ),
        ),
        const SizedBox(height: 14),
        SheetSectionLabel('Détails'),
        const SizedBox(height: 4),
        SheetStat(label: 'Vitesse', value: formatSpeed(vehicle.speed)),
        Divider(height: 1, color: TransitColors.borderSubtle),
        SheetStat(label: 'Direction', value: compassLabel(vehicle.bearing)),
        Divider(height: 1, color: TransitColors.borderSubtle),
        SheetStat(
          label: 'Dernière position',
          value: formatAge(vehicle.timestamp, now),
        ),
      ],
    );
  }
}
