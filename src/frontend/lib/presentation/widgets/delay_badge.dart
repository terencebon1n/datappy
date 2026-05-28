import 'package:flutter/material.dart';
import 'package:frontend/presentation/theme/colors.dart';

class DelayBadge extends StatelessWidget {
  const DelayBadge({super.key, required this.delaySeconds});

  final int delaySeconds;

  @override
  Widget build(BuildContext context) {
    final (Color color, String label, String sub) = switch (delaySeconds) {
      0          => (TransitColors.live, 'À l\'heure', '+0 s'),
      < 120      => (
                      TransitColors.warn,
                      '+${delaySeconds ~/ 60}m ${delaySeconds % 60}s',
                      'Léger retard',
                    ),
      _          => (
                      TransitColors.bad,
                      '+${delaySeconds ~/ 60}m ${delaySeconds % 60}s',
                      'Perturbé',
                    ),
    };

    return Column(
      crossAxisAlignment: CrossAxisAlignment.end,
      children: [
        Text(label, style: TextStyle(fontSize: 10, color: color)),
        const SizedBox(height: 2),
        Text(sub, style: const TextStyle(fontSize: 8, color: TransitColors.textMuted)),
      ],
    );
  }
}
