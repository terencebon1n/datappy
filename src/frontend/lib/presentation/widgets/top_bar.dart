import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:google_fonts/google_fonts.dart';

import 'package:frontend/application/favorites/cubit.dart';
import 'package:frontend/application/route_selection/cubit.dart';
import 'package:frontend/domain/saved_selection.dart';
import 'package:frontend/presentation/theme/colors.dart';

class TopBar extends StatelessWidget {
  const TopBar({super.key, required this.onSearchTap});

  final VoidCallback onSearchTap;

  @override
  Widget build(BuildContext context) {
    final sel      = context.watch<RouteSelectionCubit>().state;
    final stopName = sel.sourceStop ?? 'Aucun arrêt';
    final conv     = sel.selectedConveyance;
    final meta     = conv != null
        ? '${conv.shortName} · ${conv.typeName}'
        : 'Arrêt sélectionné';

    final current = sel.canSubmit
        ? SavedSelection(
            city: sel.selectedCity!,
            conveyance: sel.selectedConveyance!,
            sourceStop: sel.sourceStop!,
            destStop: sel.destStop!,
            direction: sel.direction!,
          )
        : null;
    final isSaved = current != null &&
        context.watch<FavoritesCubit>().isFavorite(current);

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
                  style: TextStyle(
                    fontSize: 9,
                    color: TransitColors.textMuted,
                    letterSpacing: 0.7,
                  ),
                ),
              ],
            ),
          ),
          _IconButton(
            icon: isSaved ? Icons.favorite_rounded : Icons.favorite_border_rounded,
            color: isSaved ? TransitColors.accent : TransitColors.textSecondary,
            onTap: current == null ? null : () => _toggleFavorite(context, current),
          ),
          const SizedBox(width: 10),
          _IconButton(
            icon: Icons.search_rounded,
            color: TransitColors.textSecondary,
            onTap: onSearchTap,
          ),
        ],
      ),
    );
  }

  void _toggleFavorite(BuildContext context, SavedSelection current) {
    final saved = context.read<FavoritesCubit>().toggle(current);
    ScaffoldMessenger.of(context)
      ..hideCurrentSnackBar()
      ..showSnackBar(
        SnackBar(
          duration: const Duration(seconds: 2),
          content: Text(saved ? 'Ajouté aux favoris' : 'Retiré des favoris'),
        ),
      );
  }
}

class _IconButton extends StatelessWidget {
  const _IconButton({required this.icon, required this.color, required this.onTap});

  final IconData icon;
  final Color color;
  final VoidCallback? onTap;

  @override
  Widget build(BuildContext context) {
    final disabled = onTap == null;
    return GestureDetector(
      onTap: onTap,
      child: Opacity(
        opacity: disabled ? 0.4 : 1,
        child: Container(
          width: 40,
          height: 40,
          decoration: BoxDecoration(
            color: TransitColors.surfaceHigh,
            borderRadius: BorderRadius.circular(12),
            border: Border.all(color: TransitColors.border),
          ),
          child: Icon(icon, color: color, size: 20),
        ),
      ),
    );
  }
}
