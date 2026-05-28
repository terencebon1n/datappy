import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:google_fonts/google_fonts.dart';

import 'package:frontend/domain/conveyance.dart';
import 'package:frontend/domain/route_type.dart';
import 'package:frontend/domain/transit_path.dart';
import 'package:frontend/application/route_selection/cubit.dart';
import 'package:frontend/application/stop_update/cubit.dart';
import 'package:frontend/application/stop_update/state.dart';
import 'package:frontend/presentation/theme/colors.dart';
import 'package:frontend/presentation/search/sheet_components.dart';

class SearchSheet extends StatelessWidget {
  const SearchSheet({super.key});

  @override
  Widget build(BuildContext context) {
    final sel = context.watch<RouteSelectionCubit>().state;
    final upd = context.watch<StopUpdateCubit>().state;

    return Container(
      decoration: const BoxDecoration(
        color: TransitColors.surface,
        borderRadius: BorderRadius.vertical(top: Radius.circular(24)),
      ),
      padding: EdgeInsets.fromLTRB(
        20, 16, 20,
        MediaQuery.of(context).viewInsets.bottom + 28,
      ),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          // Handle
          Center(
            child: Container(
              width: 36, height: 4,
              decoration: BoxDecoration(
                color: TransitColors.border,
                borderRadius: BorderRadius.circular(2),
              ),
            ),
          ),
          const SizedBox(height: 20),
          Text(
            'Sélectionner un trajet',
            style: GoogleFonts.syne(
              fontSize: 16,
              fontWeight: FontWeight.w700,
              color: TransitColors.textPrimary,
            ),
          ),
          const SizedBox(height: 18),

          const SheetLabel('Type de transport'),
          const SizedBox(height: 6),
          SheetDropdown<RouteType>(
            hint: 'Tram, Bus, Métro…',
            value: sel.selectedType,
            items: sel.routeTypes,
            label: (t) => t.name,
            onChanged: (t) {
              context.read<RouteSelectionCubit>().selectRouteType(t);
              context.read<StopUpdateCubit>().stop();
            },
          ),
          const SizedBox(height: 14),

          const SheetLabel('Ligne'),
          const SizedBox(height: 6),
          SheetDropdown<Conveyance>(
            hint: 'Sélectionnez d\'abord un type',
            value: sel.conveyances.contains(sel.selectedConveyance) ? sel.selectedConveyance : null,
            items: sel.selectedType != null ? sel.conveyances : [],
            label: (c) => c.longName,
            onChanged: sel.selectedType == null
                ? null
                : (c) {
                    context.read<RouteSelectionCubit>().selectConveyance(c);
                    context.read<StopUpdateCubit>().stop();
                  },
          ),
          const SizedBox(height: 14),

          const SheetLabel('Arrêt de départ'),
          const SizedBox(height: 6),
          SheetDropdown<String>(
            hint: 'Sélectionnez une ligne d\'abord',
            value: sel.stops.contains(sel.sourceStop) ? sel.sourceStop : null,
            items: sel.selectedConveyance != null ? sel.stops : [],
            label: (s) => s,
            onChanged: sel.selectedConveyance == null
                ? null
                : (s) => context.read<RouteSelectionCubit>().selectSourceStop(s),
          ),
          const SizedBox(height: 14),

          const SheetLabel('Destination'),
          const SizedBox(height: 6),
          SheetDropdown<String>(
            hint: 'Sélectionnez une ligne d\'abord',
            value: sel.stops.contains(sel.destStop) ? sel.destStop : null,
            items: sel.selectedConveyance != null ? sel.stops : [],
            label: (s) => s,
            onChanged: sel.selectedConveyance == null
                ? null
                : (s) => context.read<RouteSelectionCubit>().selectDestStop(s),
          ),
          const SizedBox(height: 24),

          SizedBox(
            height: 48,
            child: ElevatedButton(
              style: ElevatedButton.styleFrom(
                backgroundColor: sel.canSubmit
                    ? TransitColors.accentBg
                    : TransitColors.surfaceHigh,
                foregroundColor: sel.canSubmit
                    ? TransitColors.accent
                    : TransitColors.textMuted,
                elevation: 0,
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(14),
                  side: BorderSide(
                    color: sel.canSubmit
                        ? TransitColors.accentBorder
                        : TransitColors.border,
                  ),
                ),
              ),
              onPressed: sel.canSubmit && upd is! StopUpdateConnecting
                  ? () {
                      context.read<StopUpdateCubit>().watchStopUpdates(
                        TransitPath(
                          city: 'montpellier',
                          routeId: sel.selectedConveyance!.id,
                          direction: sel.direction!,
                        ),
                      );
                      Navigator.of(context).pop();
                    }
                  : null,
              child: upd is StopUpdateConnecting
                  ? const SizedBox(
                      width: 18, height: 18,
                      child: CircularProgressIndicator(
                        color: TransitColors.accent,
                        strokeWidth: 2,
                      ),
                    )
                  : Text(
                      'Afficher les horaires',
                      style: GoogleFonts.syne(
                        fontSize: 14,
                        fontWeight: FontWeight.w600,
                      ),
                    ),
            ),
          ),
        ],
      ),
    );
  }
}
