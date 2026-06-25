import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';

import 'package:frontend/application/route_selection/cubit.dart';
import 'package:frontend/application/route_selection/state.dart';
import 'package:frontend/domain/conveyance.dart';
import 'package:frontend/presentation/funnel/funnel_header.dart';
import 'package:frontend/presentation/funnel/funnel_widgets.dart';

class LineStep extends StatelessWidget {
  const LineStep({super.key});

  /// Group conveyances by type name, preserving the backend ordering
  /// (sorted by type then short name).
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
