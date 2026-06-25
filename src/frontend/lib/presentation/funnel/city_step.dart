import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';

import 'package:frontend/application/route_selection/cubit.dart';
import 'package:frontend/presentation/funnel/funnel_colors.dart';
import 'package:frontend/presentation/funnel/funnel_header.dart';
import 'package:frontend/presentation/funnel/funnel_widgets.dart';

class CityStep extends StatelessWidget {
  const CityStep({super.key});

  String _label(String name) =>
      name.isEmpty ? name : '${name[0].toUpperCase()}${name.substring(1)}';

  @override
  Widget build(BuildContext context) {
    final cubit = context.read<RouteSelectionCubit>();
    final cities = context.select(
      (RouteSelectionCubit c) => c.state.cities,
    );

    return Column(
      children: [
        FunnelHeader(
          overline: 'Nouvelle recherche',
          title: 'Quelle ville ?',
          leadingIsClose: true,
          onLeading: () => Navigator.of(context).maybePop(),
        ),
        Expanded(
          child: cities.isEmpty
              ? const Center(child: CircularProgressIndicator())
              : ListView(
                  padding: EdgeInsets.zero,
                  children: [
                    const FunnelSectionLabel('Réseaux disponibles'),
                    for (final city in cities)
                      InkWell(
                        onTap: () => cubit.selectCity(city),
                        child: Container(
                          decoration: const BoxDecoration(
                            border: Border(
                              bottom: BorderSide(color: FunnelColors.border, width: 0.5),
                            ),
                          ),
                          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
                          child: Row(
                            children: [
                              const Icon(Icons.location_city,
                                  size: 20, color: FunnelColors.tramAccent),
                              const SizedBox(width: 12),
                              Expanded(
                                child: Text(
                                  _label(city.name),
                                  style: const TextStyle(
                                    fontSize: 14,
                                    fontWeight: FontWeight.w500,
                                    color: FunnelColors.textPrimary,
                                  ),
                                ),
                              ),
                              const Icon(Icons.chevron_right,
                                  size: 18, color: FunnelColors.textSecondary),
                            ],
                          ),
                        ),
                      ),
                  ],
                ),
        ),
      ],
    );
  }
}
