import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

import 'package:frontend/presentation/theme/colors.dart';
import 'package:frontend/presentation/widgets/delay_badge.dart';

class DepartureRow extends StatelessWidget {
  const DepartureRow({
    super.key,
    required this.rank,
    required this.departure,
    required this.now,
    required this.opacity,
    required this.showDivider,
  });

  final int      rank;
  final dynamic  departure; // StopDeparture — departureTime: int?, arrivalDelay: int
  final DateTime now;
  final double   opacity;
  final bool     showDivider;

  @override
  Widget build(BuildContext context) {
    final int?   depTs     = departure.departureTime as int?;
    final int    delay     = (departure.arrivalDelay as int?) ?? 0;
    final String countdown = _countdown(depTs, now);
    final String absTime   = _absTime(depTs);

    return Opacity(
      opacity: opacity,
      child: Column(
        children: [
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 11),
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.center,
              children: [
                SizedBox(
                  width: 18,
                  child: Text(
                    '$rank',
                    style: TextStyle(fontSize: 10, color: TransitColors.textMuted),
                  ),
                ),
                const SizedBox(width: 6),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        countdown,
                        style: GoogleFonts.ibmPlexMono(
                          fontSize: 15,
                          fontWeight: FontWeight.w600,
                          color: TransitColors.textPrimary,
                          letterSpacing: 0.3,
                        ),
                      ),
                      const SizedBox(height: 2),
                      Text(
                        'Départ prévue · $absTime',
                        style: TextStyle(fontSize: 8.5, color: TransitColors.textMuted),
                      ),
                    ],
                  ),
                ),
                DelayBadge(delaySeconds: delay),
              ],
            ),
          ),
          if (showDivider)
            Divider(height: 1, thickness: 1, color: TransitColors.borderSubtle),
        ],
      ),
    );
  }

  static String _countdown(int? ts, DateTime now) {
    if (ts == null) return '--:--';
    final rem = ts - (now.millisecondsSinceEpoch ~/ 1000);
    if (rem <= 0)  return 'À quai';
    if (rem < 60)  return '$rem s';
    return '${rem ~/ 60} min ${(rem % 60).toString().padLeft(2, '0')} s';
  }

  static String _absTime(int? ts) {
    if (ts == null) return '--:--';
    final dt = DateTime.fromMillisecondsSinceEpoch(ts * 1000);
    return '${_p(dt.hour)}:${_p(dt.minute)}:${_p(dt.second)}';
  }

  static String _p(int n) => n.toString().padLeft(2, '0');
}
