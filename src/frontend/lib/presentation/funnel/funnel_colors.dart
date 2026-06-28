import 'package:flutter/material.dart';

import 'package:frontend/domain/gtfs_route_type.dart';

class FunnelPalette {
  final Color header;
  final Color surface;
  final Color surfaceMuted;
  final Color textPrimary;
  final Color textSecondary;
  final Color border;
  final Color selectedRowBg;
  final Color stepDoneBg;
  final Color stepDoneFg;
  final Color live;

  final Color onHeader;
  final Color onHeaderMuted;
  final Color onHeaderFaint;
  final Color headerFieldBg;

  const FunnelPalette({
    required this.header,
    required this.surface,
    required this.surfaceMuted,
    required this.textPrimary,
    required this.textSecondary,
    required this.border,
    required this.selectedRowBg,
    required this.stepDoneBg,
    required this.stepDoneFg,
    required this.live,
    required this.onHeader,
    required this.onHeaderMuted,
    required this.onHeaderFaint,
    required this.headerFieldBg,
  });
}

const lightFunnel = FunnelPalette(
  header:        Color(0xFF1B3F72),
  surface:       Color(0xFFFFFFFF),
  surfaceMuted:  Color(0xFFF2F4F7),
  textPrimary:   Color(0xFF1A1D23),
  textSecondary: Color(0xFF6B7280),
  border:        Color(0xFFE5E7EB),
  selectedRowBg: Color(0xFFE6F1FB),
  stepDoneBg:    Color(0xFFEAF3DE),
  stepDoneFg:    Color(0xFF27500A),
  live:          Color(0xFF4ADE80),
  onHeader:      Colors.white,
  onHeaderMuted: Color(0x99FFFFFF),
  onHeaderFaint: Color(0x66FFFFFF),
  headerFieldBg: Color(0x26FFFFFF),
);

const darkFunnel = FunnelPalette(
  header:        Color(0xFF13294A),
  surface:       Color(0xFF171B21),
  surfaceMuted:  Color(0xFF1F242C),
  textPrimary:   Color(0xFFE6E8EB),
  textSecondary: Color(0xFF9AA2AE),
  border:        Color(0xFF2A2F37),
  selectedRowBg: Color(0xFF14304B),
  stepDoneBg:    Color(0xFF14301E),
  stepDoneFg:    Color(0xFF7BC98F),
  live:          Color(0xFF4ADE80),
  onHeader:      Colors.white,
  onHeaderMuted: Color(0x99FFFFFF),
  onHeaderFaint: Color(0x66FFFFFF),
  headerFieldBg: Color(0x26FFFFFF),
);

abstract final class FunnelColors {
  static FunnelPalette _p = lightFunnel;

  static void apply(bool dark) => _p = dark ? darkFunnel : lightFunnel;

  static Color get header        => _p.header;
  static Color get surface       => _p.surface;
  static Color get surfaceMuted  => _p.surfaceMuted;
  static Color get textPrimary   => _p.textPrimary;
  static Color get textSecondary => _p.textSecondary;
  static Color get border        => _p.border;
  static Color get selectedRowBg => _p.selectedRowBg;
  static Color get stepDoneBg    => _p.stepDoneBg;
  static Color get stepDoneFg    => _p.stepDoneFg;
  static Color get live          => _p.live;

  static Color get onHeader      => _p.onHeader;
  static Color get onHeaderMuted => _p.onHeaderMuted;
  static Color get onHeaderFaint => _p.onHeaderFaint;
  static Color get headerFieldBg => _p.headerFieldBg;

  static const tramBg     = Color(0xFFE6F1FB);
  static const tramFg     = Color(0xFF0C447C);
  static const tramAccent = Color(0xFF185FA5);

  static const busBg = Color(0xFFEEEDFE);
  static const busFg = Color(0xFF3C3489);
}

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
  switch (GtfsRouteType.fromId(typeId)) {
    case GtfsRouteType.bus:
      return const ConveyanceStyle(
        icon: Icons.directions_bus,
        bg: FunnelColors.busBg,
        fg: FunnelColors.busFg,
        accent: FunnelColors.busFg,
      );
    case GtfsRouteType.subway:
      return _tramStyle.copyIcon(Icons.directions_subway);
    case GtfsRouteType.rail:
      return _tramStyle.copyIcon(Icons.train);
    case GtfsRouteType.ferry:
      return _tramStyle.copyIcon(Icons.directions_boat);
    case GtfsRouteType.cableCar:
    case GtfsRouteType.gondola:
    case GtfsRouteType.funicular:
      return _tramStyle.copyIcon(Icons.directions_transit);
    case GtfsRouteType.tram:
      return _tramStyle;
    case null:
      return _tramStyle.copyIcon(Icons.directions_transit);
  }
}

extension on ConveyanceStyle {
  ConveyanceStyle copyIcon(IconData icon) =>
      ConveyanceStyle(icon: icon, bg: bg, fg: fg, accent: accent);
}

Color funnelOnColor(Color background) =>
    background.computeLuminance() > 0.5 ? FunnelColors.textPrimary : Colors.white;
