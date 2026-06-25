import 'package:flutter/material.dart';

/// Light palette mirroring src/frontend/gtfsrt_flow_mockup.html.
abstract final class FunnelColors {
  static const header        = Color(0xFF1B3F72);
  static const surface       = Color(0xFFFFFFFF);
  static const surfaceMuted  = Color(0xFFF2F4F7);
  static const textPrimary   = Color(0xFF1A1D23);
  static const textSecondary = Color(0xFF6B7280);
  static const border        = Color(0xFFE5E7EB);

  // Tram / rail family (blue).
  static const tramBg     = Color(0xFFE6F1FB);
  static const tramFg     = Color(0xFF0C447C);
  static const tramAccent = Color(0xFF185FA5);

  // Bus family (purple).
  static const busBg = Color(0xFFEEEDFE);
  static const busFg = Color(0xFF3C3489);

  static const stepDoneBg = Color(0xFFEAF3DE);
  static const stepDoneFg = Color(0xFF27500A);

  static const selectedRowBg = Color(0xFFE6F1FB);
  static const live          = Color(0xFF4ADE80);

  // On-header text tints.
  static const onHeader        = Colors.white;
  static const onHeaderMuted   = Color(0x99FFFFFF); // 60% white
  static const onHeaderFaint   = Color(0x66FFFFFF); // 40% white
  static const headerFieldBg   = Color(0x26FFFFFF); // 15% white
}

/// Visual style for a conveyance, derived from its GTFS `route_type` id.
/// RouteTypeId: TRAM=0, SUBWAY=1, RAIL=2, BUS=3, FERRY=4, CABLE_CAR=5,
/// GONDOLA=6, FUNICULAR=7.
class ConveyanceStyle {
  final IconData icon;
  final Color bg;
  final Color fg;
  final Color accent;

  const ConveyanceStyle({
    required this.icon,
    required this.bg,
    required this.fg,
    required this.accent,
  });
}

const _tramStyle = ConveyanceStyle(
  icon: Icons.tram,
  bg: FunnelColors.tramBg,
  fg: FunnelColors.tramFg,
  accent: FunnelColors.tramAccent,
);

ConveyanceStyle styleForType(int typeId) {
  switch (typeId) {
    case 3: // bus
      return const ConveyanceStyle(
        icon: Icons.directions_bus,
        bg: FunnelColors.busBg,
        fg: FunnelColors.busFg,
        accent: FunnelColors.busFg,
      );
    case 1: // subway
      return _tramStyle.copyIcon(Icons.directions_subway);
    case 2: // rail
      return _tramStyle.copyIcon(Icons.train);
    case 4: // ferry
      return _tramStyle.copyIcon(Icons.directions_boat);
    case 5: // cable car
    case 6: // gondola
    case 7: // funicular
      return _tramStyle.copyIcon(Icons.directions_transit);
    case 0: // tram
    default:
      return _tramStyle;
  }
}

extension on ConveyanceStyle {
  ConveyanceStyle copyIcon(IconData icon) =>
      ConveyanceStyle(icon: icon, bg: bg, fg: fg, accent: accent);
}

/// Readable foreground (black/white) for text drawn on [background].
Color funnelOnColor(Color background) =>
    background.computeLuminance() > 0.5 ? FunnelColors.textPrimary : Colors.white;
