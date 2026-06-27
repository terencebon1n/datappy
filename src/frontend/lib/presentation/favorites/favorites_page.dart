import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:google_fonts/google_fonts.dart';

import 'package:frontend/application/favorites/cubit.dart';
import 'package:frontend/domain/saved_selection.dart';
import 'package:frontend/presentation/theme/colors.dart';
import 'package:frontend/presentation/funnel/funnel_widgets.dart' show RouteBadge;

/// The "Favoris" tab: a list of saved searches. Tapping one loads it back onto
/// the dashboard (via [onSelect]); each can be removed by swiping or the trash
/// button.
class FavoritesPage extends StatelessWidget {
  const FavoritesPage({super.key, required this.onSelect});

  final ValueChanged<SavedSelection> onSelect;

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        Padding(
          padding: const EdgeInsets.fromLTRB(16, 14, 16, 10),
          child: Text(
            'Favoris',
            style: GoogleFonts.syne(
              fontSize: 20,
              fontWeight: FontWeight.w700,
              color: TransitColors.textPrimary,
              letterSpacing: -0.3,
            ),
          ),
        ),
        Expanded(
          child: BlocBuilder<FavoritesCubit, List<SavedSelection>>(
            builder: (context, favorites) {
              if (favorites.isEmpty) return const _EmptyState();
              return ListView.separated(
                padding: const EdgeInsets.fromLTRB(14, 4, 14, 100),
                itemCount: favorites.length,
                separatorBuilder: (_, _) => const SizedBox(height: 10),
                itemBuilder: (context, i) {
                  final fav = favorites[i];
                  return Dismissible(
                    key: ValueKey(fav.hashCode),
                    direction: DismissDirection.endToStart,
                    background: const _DismissBackground(),
                    onDismissed: (_) =>
                        context.read<FavoritesCubit>().remove(fav),
                    child: _FavoriteTile(
                      favorite: fav,
                      onTap: () => onSelect(fav),
                      onDelete: () =>
                          context.read<FavoritesCubit>().remove(fav),
                    ),
                  );
                },
              );
            },
          ),
        ),
      ],
    );
  }
}

class _FavoriteTile extends StatelessWidget {
  const _FavoriteTile({
    required this.favorite,
    required this.onTap,
    required this.onDelete,
  });

  final SavedSelection favorite;
  final VoidCallback onTap;
  final VoidCallback onDelete;

  @override
  Widget build(BuildContext context) {
    return Material(
      color: TransitColors.surface,
      borderRadius: BorderRadius.circular(14),
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(14),
        child: Container(
          padding: const EdgeInsets.all(14),
          decoration: BoxDecoration(
            borderRadius: BorderRadius.circular(14),
            border: Border.all(color: TransitColors.border),
          ),
          child: Row(
            children: [
              RouteBadge(favorite.conveyance),
              const SizedBox(width: 12),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      '${favorite.sourceStop} → ${favorite.destStop}',
                      maxLines: 2,
                      overflow: TextOverflow.ellipsis,
                      style: GoogleFonts.syne(
                        fontSize: 13,
                        fontWeight: FontWeight.w600,
                        color: TransitColors.textPrimary,
                      ),
                    ),
                    const SizedBox(height: 2),
                    Text(
                      favorite.city.name.toUpperCase(),
                      style: TextStyle(
                        fontSize: 9,
                        color: TransitColors.textMuted,
                        letterSpacing: 0.7,
                      ),
                    ),
                  ],
                ),
              ),
              IconButton(
                onPressed: onDelete,
                visualDensity: VisualDensity.compact,
                icon: Icon(
                  Icons.delete_outline_rounded,
                  size: 20,
                  color: TransitColors.textMuted,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _DismissBackground extends StatelessWidget {
  const _DismissBackground();

  @override
  Widget build(BuildContext context) {
    return Container(
      alignment: Alignment.centerRight,
      padding: const EdgeInsets.only(right: 20),
      decoration: BoxDecoration(
        color: TransitColors.bad,
        borderRadius: BorderRadius.circular(14),
      ),
      child: const Icon(Icons.delete_rounded, color: Colors.white, size: 22),
    );
  }
}

class _EmptyState extends StatelessWidget {
  const _EmptyState();

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 40),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(
              Icons.favorite_border_rounded,
              size: 40,
              color: TransitColors.textMuted,
            ),
            const SizedBox(height: 12),
            Text(
              'Aucun favori',
              textAlign: TextAlign.center,
              style: GoogleFonts.syne(
                fontSize: 15,
                fontWeight: FontWeight.w600,
                color: TransitColors.textSecondary,
              ),
            ),
            const SizedBox(height: 6),
            Text(
              "Enregistrez une recherche depuis l'accueil avec l'icône ♥.",
              textAlign: TextAlign.center,
              style: TextStyle(fontSize: 12, color: TransitColors.textMuted),
            ),
          ],
        ),
      ),
    );
  }
}
