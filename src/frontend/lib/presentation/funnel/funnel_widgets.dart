import 'package:flutter/material.dart';

import 'package:frontend/domain/conveyance.dart';
import 'package:frontend/presentation/funnel/funnel_colors.dart';

/// Small uppercase section label (mockup `.slabel` style, dark variant).
class FunnelSectionLabel extends StatelessWidget {
  const FunnelSectionLabel(this.text, {super.key});
  final String text;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.fromLTRB(16, 12, 16, 8),
      child: Text(
        text.toUpperCase(),
        style: const TextStyle(
          fontSize: 10,
          fontWeight: FontWeight.w600,
          letterSpacing: 0.4,
          color: FunnelColors.textSecondary,
        ),
      ),
    );
  }
}

/// Extended, human-readable route label: `{route_id} - {route_long_name}`.
String routeExtendedName(Conveyance c) =>
    c.longName.isNotEmpty ? '${c.id} - ${c.longName}' : c.id;

/// Colored pill showing a route's short name in its own GTFS colour.
/// Falls back to the type palette when the route has no (near-white) colour.
class RouteBadge extends StatelessWidget {
  const RouteBadge(this.conveyance, {super.key, this.fontSize = 12});

  final Conveyance conveyance;
  final double fontSize;

  @override
  Widget build(BuildContext context) {
    final style = styleForType(conveyance.typeId);
    final routeColor = Color(conveyance.colorValue);
    final faint = routeColor.computeLuminance() > 0.85;
    final bg = faint ? style.bg : routeColor;
    final fg = faint ? style.fg : funnelOnColor(routeColor);

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
      decoration: BoxDecoration(
        color: bg,
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: Colors.black12),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(style.icon, size: fontSize + 1, color: fg),
          if (conveyance.shortName.isNotEmpty) ...[
            const SizedBox(width: 4),
            Text(
              conveyance.shortName,
              style: TextStyle(
                fontSize: fontSize,
                fontWeight: FontWeight.w600,
                color: fg,
              ),
            ),
          ],
        ],
      ),
    );
  }
}

/// A tappable route row: coloured badge + `{id} - {long name}`.
class RouteListTile extends StatelessWidget {
  const RouteListTile({
    super.key,
    required this.conveyance,
    required this.onTap,
  });

  final Conveyance conveyance;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    return InkWell(
      onTap: onTap,
      child: Container(
        decoration: const BoxDecoration(
          border: Border(bottom: BorderSide(color: FunnelColors.border, width: 0.5)),
        ),
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
        child: Row(
          children: [
            RouteBadge(conveyance),
            const SizedBox(width: 12),
            Expanded(
              child: Text(
                routeExtendedName(conveyance),
                maxLines: 2,
                overflow: TextOverflow.ellipsis,
                style: const TextStyle(fontSize: 13, color: FunnelColors.textPrimary),
              ),
            ),
            const Icon(Icons.chevron_right, size: 18, color: FunnelColors.textSecondary),
          ],
        ),
      ),
    );
  }
}

/// Running selection shown at the top of later funnel steps so the user can
/// confirm what they picked. Shows the line, plus the origin on the dest step.
class FunnelSelectionBar extends StatelessWidget {
  const FunnelSelectionBar({super.key, required this.line, this.origin});

  final Conveyance line;
  final String? origin;

  @override
  Widget build(BuildContext context) {
    return Container(
      width: double.infinity,
      color: FunnelColors.surfaceMuted,
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              RouteBadge(line, fontSize: 11),
              const SizedBox(width: 8),
              Expanded(
                child: Text(
                  routeExtendedName(line),
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                  style: const TextStyle(
                    fontSize: 12,
                    fontWeight: FontWeight.w500,
                    color: FunnelColors.textPrimary,
                  ),
                ),
              ),
            ],
          ),
          if (origin != null)
            Padding(
              padding: const EdgeInsets.only(top: 6),
              child: Row(
                children: [
                  const Icon(Icons.trip_origin, size: 13, color: FunnelColors.tramAccent),
                  const SizedBox(width: 6),
                  Expanded(
                    child: Text(
                      'Départ · $origin',
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                      style: const TextStyle(fontSize: 12, color: FunnelColors.textSecondary),
                    ),
                  ),
                ],
              ),
            ),
        ],
      ),
    );
  }
}
