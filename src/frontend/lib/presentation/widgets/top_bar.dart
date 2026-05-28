import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:google_fonts/google_fonts.dart';

import 'package:frontend/application/route_selection/cubit.dart';
import 'package:frontend/presentation/theme/colors.dart';

class TopBar extends StatelessWidget {
  const TopBar({super.key, required this.onSearchTap});

  final VoidCallback onSearchTap;

  @override
  Widget build(BuildContext context) {
    final sel      = context.watch<RouteSelectionCubit>().state;
    final stopName = sel.sourceStop ?? 'Aucun arrêt';
    final meta     = sel.selectedType?.name ?? 'Arrêt sélectionné';

    return Padding(
      padding: const EdgeInsets.fromLTRB(16, 14, 16, 10),
      child: Row(
        children: [
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  stopName,
                  style: GoogleFonts.syne(
                    fontSize: 20,
                    fontWeight: FontWeight.w700,
                    color: TransitColors.textPrimary,
                    letterSpacing: -0.3,
                  ),
                ),
                const SizedBox(height: 2),
                Text(
                  meta.toUpperCase(),
                  style: const TextStyle(
                    fontSize: 9,
                    color: TransitColors.textMuted,
                    letterSpacing: 0.7,
                  ),
                ),
              ],
            ),
          ),
          GestureDetector(
            onTap: onSearchTap,
            child: Container(
              width: 40,
              height: 40,
              decoration: BoxDecoration(
                color: TransitColors.surfaceHigh,
                borderRadius: BorderRadius.circular(12),
                border: Border.all(color: TransitColors.border),
              ),
              child: const Icon(
                Icons.search_rounded,
                color: TransitColors.textSecondary,
                size: 20,
              ),
            ),
          ),
        ],
      ),
    );
  }
}
