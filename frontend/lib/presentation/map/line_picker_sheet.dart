import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';

import 'package:frontend/application/vehicle_map/cubit.dart';
import 'package:frontend/domain/conveyance.dart';
import 'package:frontend/presentation/funnel/funnel_widgets.dart';
import 'package:frontend/presentation/map/sheet_widgets.dart';
import 'package:frontend/presentation/theme/colors.dart';

Map<String, List<Conveyance>> groupLinesByType(List<Conveyance> lines) {
  final grouped = <String, List<Conveyance>>{};
  for (final line in lines) {
    grouped.putIfAbsent(line.typeName, () => []).add(line);
  }
  return grouped;
}

Future<void> openLinePicker(BuildContext context) {
  final cubit = context.read<VehicleMapCubit>();

  return showModalBottomSheet<void>(
    context: context,
    backgroundColor: Colors.transparent,
    isScrollControlled: true,
    builder: (sheetContext) => BlocProvider.value(
      value: cubit,
      child: LinePickerSheet(
        onSelected: (line) {
          cubit.selectLine(line);
          Navigator.of(sheetContext).pop();
        },
      ),
    ),
  );
}

class LinePickerSheet extends StatelessWidget {
  const LinePickerSheet({super.key, required this.onSelected});

  final ValueChanged<Conveyance> onSelected;

  @override
  Widget build(BuildContext context) {
    final state = context.watch<VehicleMapCubit>().state;
    final groups = groupLinesByType(state.lines);

    return SheetShell(
      children: [
        SheetTitle(
          icon: Icons.alt_route_rounded,
          iconColor: TransitColors.accent,
          title: 'Choisir une ligne',
        ),
        const SizedBox(height: 12),
        if (state.lines.isEmpty)
          SheetEmpty(text: 'Aucune ligne disponible.')
        else
          Flexible(
            child: ListView(
              shrinkWrap: true,
              padding: EdgeInsets.zero,
              children: [
                for (final entry in groups.entries) ...[
                  Padding(
                    padding: const EdgeInsets.only(top: 4, bottom: 6),
                    child: SheetSectionLabel(entry.key),
                  ),
                  for (final line in entry.value)
                    _PickerRow(
                      line: line,
                      selected: line.id == state.line?.id,
                      onTap: () => onSelected(line),
                    ),
                ],
              ],
            ),
          ),
      ],
    );
  }
}

class _PickerRow extends StatelessWidget {
  const _PickerRow({
    required this.line,
    required this.selected,
    required this.onTap,
  });

  final Conveyance line;
  final bool selected;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    return Container(
      color: selected ? TransitColors.accentBg : null,
      child: RouteListTile(conveyance: line, onTap: onTap),
    );
  }
}
