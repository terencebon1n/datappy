import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

import 'package:frontend/presentation/theme/colors.dart';
import 'package:frontend/presentation/funnel/funnel_colors.dart';

List<Color> _transitGetters() => [
      TransitColors.bg,
      TransitColors.surface,
      TransitColors.surfaceHigh,
      TransitColors.border,
      TransitColors.borderSubtle,
      TransitColors.textPrimary,
      TransitColors.textSecondary,
      TransitColors.textMuted,
      TransitColors.accent,
      TransitColors.accentBg,
      TransitColors.accentBorder,
      TransitColors.live,
      TransitColors.liveBg,
      TransitColors.liveBorder,
      TransitColors.warn,
      TransitColors.bad,
    ];

List<Color> _funnelGetters() => [
      FunnelColors.header,
      FunnelColors.surface,
      FunnelColors.surfaceMuted,
      FunnelColors.textPrimary,
      FunnelColors.textSecondary,
      FunnelColors.border,
      FunnelColors.selectedRowBg,
      FunnelColors.stepDoneBg,
      FunnelColors.stepDoneFg,
      FunnelColors.live,
      FunnelColors.onHeader,
      FunnelColors.onHeaderMuted,
      FunnelColors.onHeaderFaint,
      FunnelColors.headerFieldBg,
    ];

void main() {
  tearDown(() {
    TransitColors.apply(false);
    FunnelColors.apply(false);
  });

  test('TransitColors switches palettes on apply', () {
    TransitColors.apply(false);
    expect(TransitColors.bg, lightTransit.bg);
    final light = _transitGetters();

    TransitColors.apply(true);
    expect(TransitColors.bg, darkTransit.bg);
    final dark = _transitGetters();

    expect(dark, isNot(equals(light)));
  });

  test('FunnelColors switches palettes on apply', () {
    FunnelColors.apply(false);
    expect(FunnelColors.header, lightFunnel.header);
    final light = _funnelGetters();

    FunnelColors.apply(true);
    expect(FunnelColors.header, darkFunnel.header);
    final dark = _funnelGetters();

    expect(dark.length, light.length);
  });
}
