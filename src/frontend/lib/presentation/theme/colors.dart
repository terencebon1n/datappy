import 'package:flutter/material.dart';

/// Light theme for the dashboard, aligned with the funnel's palette
/// (see presentation/funnel/funnel_colors.dart).
abstract final class TransitColors {
  // Surfaces
  static const bg            = Color(0xFFF4F6F9); // app background (light grey)
  static const surface       = Color(0xFFFFFFFF); // cards / panels
  static const surfaceHigh   = Color(0xFFF2F4F7); // inputs / elevated chips
  static const border        = Color(0xFFE5E7EB);
  static const borderSubtle  = Color(0xFFEDF0F4);

  // Text
  static const textPrimary   = Color(0xFF1A1D23);
  static const textSecondary = Color(0xFF6B7280);
  static const textMuted     = Color(0xFF9AA2AE);

  // Accent (blue, matching the funnel)
  static const accent        = Color(0xFF185FA5);
  static const accentBg      = Color(0xFFE6F1FB);
  static const accentBorder  = Color(0xFFB5D4F4);

  // Live (green)
  static const live          = Color(0xFF1E8E3E);
  static const liveBg        = Color(0xFFEAF3DE);
  static const liveBorder    = Color(0xFFC9E2B0);

  // Status
  static const warn          = Color(0xFFB45309);
  static const bad           = Color(0xFFC0392B);
}
