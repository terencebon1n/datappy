import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';

import 'package:frontend/application/nearby/cubit.dart';
import 'package:frontend/application/route_selection/cubit.dart';
import 'package:frontend/application/route_selection/state.dart';
import 'package:frontend/domain/conveyance.dart';
import 'package:frontend/presentation/funnel/funnel_colors.dart';
import 'package:frontend/presentation/funnel/funnel_header.dart';
import 'package:frontend/presentation/funnel/funnel_widgets.dart';

class LineStep extends StatelessWidget {
  const LineStep({super.key});

  Map<String, List<Conveyance>> _grouped(List<Conveyance> items) {
    final groups = <String, List<Conveyance>>{};
    for (final c in items) {
      groups.putIfAbsent(c.typeName, () => []).add(c);
    }
    return groups;
  }

  @override
  Widget build(BuildContext context) {
    final cubit = context.read<RouteSelectionCubit>();
    final state = context.watch<RouteSelectionCubit>().state;
    final conveyances = state.conveyances;
    final groups = _grouped(conveyances);
    final cityName = state.selectedCity?.name ?? '';

    return Column(
      children: [
        FunnelHeader(
          overline: cityName.isEmpty ? 'Nouvelle recherche' : cityName,
          title: 'Quelle ligne ?',
          stepperFor: FunnelStep.line,
          onLeading: cubit.back,
        ),
        _NearbyEntry(
          onTap: () {
            context.read<NearbyCubit>().findNearby(state.selectedCity!);
            cubit.browseNearby();
          },
        ),
        Expanded(
          child: conveyances.isEmpty
              ? const Center(child: CircularProgressIndicator())
              : ListView(
                  padding: const EdgeInsets.only(bottom: 16),
                  children: [
                    for (final entry in groups.entries) ...[
                      FunnelSectionLabel(entry.key),
                      for (final c in entry.value)
                        RouteListTile(
                          conveyance: c,
                          onTap: () => cubit.selectConveyance(c),
                        ),
                    ],
                  ],
                ),
        ),
      ],
    );
  }
}

class _NearbyEntry extends StatelessWidget {
  const _NearbyEntry({required this.onTap});

  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    return InkWell(
      onTap: onTap,
      child: Container(
        width: double.infinity,
        color: FunnelColors.surfaceMuted,
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
        child: Row(
          children: [
            const Icon(Icons.my_location, size: 18, color: FunnelColors.tramAccent),
            const SizedBox(width: 12),
            Expanded(
              child: Text(
                'Autour de moi',
                style: TextStyle(
                  fontSize: 14,
                  fontWeight: FontWeight.w600,
                  color: FunnelColors.textPrimary,
                ),
              ),
            ),
            Icon(Icons.chevron_right, size: 18, color: FunnelColors.textSecondary),
          ],
        ),
      ),
    );
  }
}
