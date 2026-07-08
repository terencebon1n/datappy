import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

import 'package:frontend/presentation/funnel/funnel_colors.dart';

void main() {
  group('styleForType', () {
    test('bus uses its own icon and palette', () {
      final style = styleForType(3);
      expect(style.icon, Icons.directions_bus);
      expect(style.bg, FunnelColors.busBg);
    });

    test('tram uses the tram icon and blue palette', () {
      final style = styleForType(0);
      expect(style.icon, Icons.tram);
      expect(style.bg, FunnelColors.tramBg);
    });

    test('each rail-family type maps to a distinct icon on the tram palette', () {
      expect(styleForType(1).icon, Icons.directions_subway);
      expect(styleForType(2).icon, Icons.train);
      expect(styleForType(4).icon, Icons.directions_boat);
      for (final cableLike in [5, 6, 7]) {
        expect(styleForType(cableLike).icon, Icons.directions_transit);
        expect(styleForType(cableLike).bg, FunnelColors.tramBg);
      }
    });

    test('unknown types fall back to a generic transit style', () {
      final style = styleForType(99);
      expect(style.icon, Icons.directions_transit);
      expect(style.bg, FunnelColors.tramBg);
    });
  });

  group('funnelOnColor', () {
    test('dark background gets white text', () {
      expect(funnelOnColor(const Color(0xFF000000)), Colors.white);
    });

    test('light background gets the primary text color', () {
      FunnelColors.apply(false);
      expect(funnelOnColor(const Color(0xFFFFFFFF)), FunnelColors.textPrimary);
    });
  });
}
