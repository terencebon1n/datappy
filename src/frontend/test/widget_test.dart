import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

import 'package:frontend/presentation/funnel/funnel_colors.dart';

void main() {
  group('styleForType', () {
    test('bus (type 3) uses the bus icon and purple palette', () {
      final style = styleForType(3);
      expect(style.icon, Icons.directions_bus);
      expect(style.bg, FunnelColors.busBg);
    });

    test('tram (type 0) uses the tram icon and blue palette', () {
      final style = styleForType(0);
      expect(style.icon, Icons.tram);
      expect(style.bg, FunnelColors.tramBg);
    });

    test('unknown types fall back to the tram style', () {
      final style = styleForType(99);
      expect(style.icon, Icons.tram);
      expect(style.bg, FunnelColors.tramBg);
    });
  });
}
