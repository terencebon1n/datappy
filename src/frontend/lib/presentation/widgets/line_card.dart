import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:google_fonts/google_fonts.dart';

import 'package:frontend/application/route_selection/cubit.dart';
import 'package:frontend/application/stop_update/cubit.dart';
import 'package:frontend/application/stop_update/state.dart';
import 'package:frontend/presentation/theme/colors.dart';
import 'package:frontend/presentation/widgets/live_pill.dart';

class LineCard extends StatelessWidget {
  const LineCard({super.key, required this.now});

  final DateTime now;

  @override
  Widget build(BuildContext context) {
    final sel    = context.watch<RouteSelectionCubit>().state;
    final upd    = context.watch<StopUpdateCubit>().state;
    final isLive = upd is StopUpdateLive;

    final lineLabel = sel.selectedConveyance?.shortName
                    ?? sel.selectedConveyance?.id
                    ?? '—';
    final lineColor = sel.selectedConveyance?.color;
    final dest = sel.destStop ?? 'Destination non sélectionnée';
    final via  = sel.selectedConveyance?.longName ?? '';

    return Container(
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: TransitColors.surface,
        borderRadius: BorderRadius.circular(14),
        border: Border.all(color: TransitColors.border),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              _LineBadge(label: lineLabel, color: lineColor ?? TransitColors.accentBorder),
              const SizedBox(width: 10),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      '→ $dest',
                      style: GoogleFonts.syne(
                        fontSize: 13,
                        fontWeight: FontWeight.w600,
                        color: TransitColors.textPrimary,
                      ),
                    ),
                    if (via.isNotEmpty) ...[
                      const SizedBox(height: 2),
                      Text(via, style: const TextStyle(fontSize: 9, color: TransitColors.textMuted)),
                    ],
                  ],
                ),
              ),
            ],
          ),
          const SizedBox(height: 10),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              LivePill(isLive: isLive),
              if (isLive)
                Text(
                  '${_p(now.hour)}:${_p(now.minute)}:${_p(now.second)}',
                  style: GoogleFonts.ibmPlexMono(fontSize: 11, color: TransitColors.live),
                ),
            ],
          ),
        ],
      ),
    );
  }

  static String _p(int n) => n.toString().padLeft(2, '0');
}

class _LineBadge extends StatelessWidget {
  const _LineBadge({
    required this.label,
    required this.color,
  });

  final String label;
  final Color color;

  @override
  Widget build(BuildContext context) {
    return Container(
      width: 38, height: 38,
      decoration: BoxDecoration(
        color: Color.lerp(color, Colors.black, 0.5),
        borderRadius: BorderRadius.circular(11),
        border: Border.all(color: color, width: 1.5),
      ),
      alignment: Alignment.center,
      child: Text(
        label,
        style: GoogleFonts.syne(
          fontSize: 13,
          fontWeight: FontWeight.w700,
          color: Color.lerp(color, Colors.white, 0.5),
        ),
      ),
    );
  }
}
