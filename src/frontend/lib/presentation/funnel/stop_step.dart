import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';

import 'package:frontend/application/route_selection/cubit.dart';
import 'package:frontend/application/route_selection/state.dart';
import 'package:frontend/presentation/funnel/funnel_colors.dart';
import 'package:frontend/presentation/funnel/funnel_header.dart';
import 'package:frontend/presentation/funnel/funnel_widgets.dart';

/// Stop picker, shared by the "Départ" (source) and "Arrivée" (dest) steps.
/// A single tap commits the stop: source advances to dest, dest resolves the
/// direction and the funnel auto-closes (see FunnelPage's listener).
class StopStep extends StatefulWidget {
  const StopStep({super.key, required this.isSource});

  final bool isSource;

  @override
  State<StopStep> createState() => _StopStepState();
}

class _StopStepState extends State<StopStep> {
  final _searchCtrl = TextEditingController();
  String _query = '';

  @override
  void dispose() {
    _searchCtrl.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final cubit = context.read<RouteSelectionCubit>();
    final state = context.watch<RouteSelectionCubit>().state;
    final conv = state.selectedConveyance;
    final cityName = state.selectedCity?.name ?? '';

    // On the arrival step, the chosen departure can't also be the arrival.
    var stops = state.stops;
    if (!widget.isSource) {
      stops = stops.where((s) => s != state.sourceStop).toList();
    }
    final filtered = _query.isEmpty
        ? stops
        : stops
            .where((s) => s.toLowerCase().contains(_query.toLowerCase()))
            .toList();

    final selectedStop = widget.isSource ? null : state.destStop;
    final resolving = !widget.isSource &&
        state.destStop != null &&
        state.destStop != state.sourceStop &&
        state.direction == null;

    return Stack(
      children: [
        Column(
          children: [
            FunnelHeader(
              overline: cityName,
              title: widget.isSource ? 'Arrêt de départ' : "Arrêt d'arrivée",
              stepperFor: widget.isSource ? FunnelStep.source : FunnelStep.dest,
              onLeading: cubit.back,
              bottom: _SearchField(
                controller: _searchCtrl,
                onChanged: (v) => setState(() => _query = v),
              ),
            ),
            if (conv != null)
              FunnelSelectionBar(
                line: conv,
                origin: widget.isSource ? null : state.sourceStop,
              ),
            Expanded(
              child: state.stops.isEmpty
                  ? const Center(child: CircularProgressIndicator())
                  : ListView(
                      padding: const EdgeInsets.only(bottom: 16),
                      children: [
                        FunnelSectionLabel(
                          widget.isSource
                              ? 'Choisissez le départ'
                              : "Choisissez l'arrivée",
                        ),
                        if (filtered.isEmpty)
                          const Padding(
                            padding: EdgeInsets.fromLTRB(16, 8, 16, 8),
                            child: Text(
                              'Aucun arrêt trouvé',
                              style: TextStyle(
                                  fontSize: 13, color: FunnelColors.textSecondary),
                            ),
                          ),
                        for (final stop in filtered)
                          _StopRow(
                            name: stop,
                            selected: stop == selectedStop,
                            onTap: () {
                              if (widget.isSource) {
                                cubit.selectSourceStop(stop);
                              } else {
                                cubit.selectDestStop(stop);
                              }
                            },
                          ),
                      ],
                    ),
            ),
          ],
        ),
        if (resolving) const _ResolvingOverlay(),
      ],
    );
  }
}

class _SearchField extends StatelessWidget {
  const _SearchField({required this.controller, required this.onChanged});
  final TextEditingController controller;
  final ValueChanged<String> onChanged;

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: BoxDecoration(
        color: FunnelColors.headerFieldBg,
        borderRadius: BorderRadius.circular(12),
      ),
      padding: const EdgeInsets.symmetric(horizontal: 10),
      child: Row(
        children: [
          const Icon(Icons.search, size: 16, color: FunnelColors.onHeaderFaint),
          const SizedBox(width: 7),
          Expanded(
            child: TextField(
              controller: controller,
              onChanged: onChanged,
              style: const TextStyle(color: Colors.white, fontSize: 13),
              cursorColor: Colors.white,
              decoration: const InputDecoration(
                isDense: true,
                border: InputBorder.none,
                hintText: 'Rechercher un arrêt…',
                hintStyle:
                    TextStyle(color: FunnelColors.onHeaderFaint, fontSize: 13),
              ),
            ),
          ),
        ],
      ),
    );
  }
}

class _StopRow extends StatelessWidget {
  const _StopRow({
    required this.name,
    required this.selected,
    required this.onTap,
  });

  final String name;
  final bool selected;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    return InkWell(
      onTap: onTap,
      child: Container(
        decoration: BoxDecoration(
          color: selected ? FunnelColors.selectedRowBg : null,
          border: const Border(
            bottom: BorderSide(color: FunnelColors.border, width: 0.5),
          ),
        ),
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
        child: Row(
          children: [
            Container(
              width: 8,
              height: 8,
              decoration: BoxDecoration(
                shape: BoxShape.circle,
                color: selected ? FunnelColors.tramFg : const Color(0xFFB5D4F4),
              ),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: Text(
                name,
                style: TextStyle(
                  fontSize: 13,
                  fontWeight: selected ? FontWeight.w600 : FontWeight.w400,
                  color: selected ? FunnelColors.tramFg : FunnelColors.textPrimary,
                ),
              ),
            ),
            Icon(
              selected ? Icons.check : Icons.chevron_right,
              size: 16,
              color: selected ? FunnelColors.tramFg : FunnelColors.textSecondary,
            ),
          ],
        ),
      ),
    );
  }
}

class _ResolvingOverlay extends StatelessWidget {
  const _ResolvingOverlay();

  @override
  Widget build(BuildContext context) {
    return const Positioned.fill(
      child: ColoredBox(
        color: Color(0xCCFFFFFF),
        child: Center(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              CircularProgressIndicator(color: FunnelColors.header),
              SizedBox(height: 12),
              Text(
                'Recherche des horaires…',
                style: TextStyle(
                  fontSize: 13,
                  fontWeight: FontWeight.w500,
                  color: FunnelColors.textPrimary,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
