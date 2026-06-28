import 'package:flutter/material.dart';

class TransitPalette {
  final Color bg;
  final Color surface;
  final Color surfaceHigh;
  final Color border;
  final Color borderSubtle;

  final Color textPrimary;
  final Color textSecondary;
  final Color textMuted;

  final Color accent;
  final Color accentBg;
  final Color accentBorder;

  final Color live;
  final Color liveBg;
  final Color liveBorder;

  final Color warn;
  final Color bad;

  const TransitPalette({
    required this.bg,
    required this.surface,
    required this.surfaceHigh,
    required this.border,
    required this.borderSubtle,
    required this.textPrimary,
    required this.textSecondary,
    required this.textMuted,
    required this.accent,
    required this.accentBg,
    required this.accentBorder,
    required this.live,
    required this.liveBg,
    required this.liveBorder,
    required this.warn,
    required this.bad,
  });
}

const lightTransit = TransitPalette(
  bg:            Color(0xFFF4F6F9),
  surface:       Color(0xFFFFFFFF),
  surfaceHigh:   Color(0xFFF2F4F7),
  border:        Color(0xFFE5E7EB),
  borderSubtle:  Color(0xFFEDF0F4),
  textPrimary:   Color(0xFF1A1D23),
  textSecondary: Color(0xFF6B7280),
  textMuted:     Color(0xFF9AA2AE),
  accent:        Color(0xFF185FA5),
  accentBg:      Color(0xFFE6F1FB),
  accentBorder:  Color(0xFFB5D4F4),
  live:          Color(0xFF1E8E3E),
  liveBg:        Color(0xFFEAF3DE),
  liveBorder:    Color(0xFFC9E2B0),
  warn:          Color(0xFFB45309),
  bad:           Color(0xFFC0392B),
);

const darkTransit = TransitPalette(
  bg:            Color(0xFF0E1116),
  surface:       Color(0xFF171B21),
  surfaceHigh:   Color(0xFF1F242C),
  border:        Color(0xFF2A2F37),
  borderSubtle:  Color(0xFF222730),
  textPrimary:   Color(0xFFE6E8EB),
  textSecondary: Color(0xFF9AA2AE),
  textMuted:     Color(0xFF6B7280),
  accent:        Color(0xFF4F9CE8),
  accentBg:      Color(0xFF14304B),
  accentBorder:  Color(0xFF1E4D7A),
  live:          Color(0xFF4ADE80),
  liveBg:        Color(0xFF14301E),
  liveBorder:    Color(0xFF1E5536),
  warn:          Color(0xFFE0A85B),
  bad:           Color(0xFFE2675B),
);

abstract final class TransitColors {
  static TransitPalette _p = lightTransit;

  static void apply(bool dark) => _p = dark ? darkTransit : lightTransit;

  static Color get bg            => _p.bg;
  static Color get surface       => _p.surface;
  static Color get surfaceHigh   => _p.surfaceHigh;
  static Color get border        => _p.border;
  static Color get borderSubtle  => _p.borderSubtle;

  static Color get textPrimary   => _p.textPrimary;
  static Color get textSecondary => _p.textSecondary;
  static Color get textMuted     => _p.textMuted;

  static Color get accent        => _p.accent;
  static Color get accentBg      => _p.accentBg;
  static Color get accentBorder  => _p.accentBorder;

  static Color get live          => _p.live;
  static Color get liveBg        => _p.liveBg;
  static Color get liveBorder    => _p.liveBorder;

  static Color get warn          => _p.warn;
  static Color get bad           => _p.bad;
}
