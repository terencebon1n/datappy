import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';

import 'package:frontend/application/theme/cubit.dart';
import 'package:frontend/presentation/theme/colors.dart';

class BottomNav extends StatelessWidget {
  const BottomNav({super.key, required this.index, required this.onTap});

  final int                index;
  final ValueChanged<int>  onTap;

  @override
  Widget build(BuildContext context) {
    final isDark = resolveIsDark(context.watch<ThemeCubit>().state);

    return Padding(
      padding: EdgeInsets.fromLTRB(
        12, 0, 12, MediaQuery.of(context).padding.bottom + 10,
      ),
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 4, vertical: 8),
        decoration: BoxDecoration(
          color: TransitColors.surface,
          borderRadius: BorderRadius.circular(22),
          border: Border.all(color: TransitColors.border),
        ),
        child: Row(
          mainAxisAlignment: MainAxisAlignment.spaceAround,
          children: [
            _NavItem(icon: Icons.favorite_rounded, label: 'Favoris', active: index == 0, onTap: () => onTap(0)),
            _NavItem(
              icon: isDark ? Icons.light_mode_rounded : Icons.dark_mode_rounded,
              label: 'Thème',
              active: false,
              onTap: () => context.read<ThemeCubit>().toggle(),
            ),
          ],
        ),
      ),
    );
  }
}

class _NavItem extends StatelessWidget {
  const _NavItem({
    required this.icon,
    required this.label,
    required this.active,
    required this.onTap,
  });

  final IconData     icon;
  final String       label;
  final bool         active;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    final color = active ? TransitColors.accent : TransitColors.textMuted;

    return GestureDetector(
      onTap: onTap,
      behavior: HitTestBehavior.opaque,
      child: SizedBox(
        width: 64,
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            AnimatedContainer(
              duration: const Duration(milliseconds: 180),
              width: 44, height: 44,
              decoration: BoxDecoration(
                color: active ? TransitColors.accentBg : Colors.transparent,
                borderRadius: BorderRadius.circular(14),
                border: active ? Border.all(color: TransitColors.accentBorder) : null,
              ),
              child: Icon(icon, color: color, size: 22),
            ),
            const SizedBox(height: 4),
            Text(label, style: TextStyle(fontSize: 9, color: color, letterSpacing: 0.3)),
          ],
        ),
      ),
    );
  }
}
