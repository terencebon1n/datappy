import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';

import 'package:frontend/application/stop_update/cubit.dart';
import 'package:frontend/application/stop_update/state.dart';
import 'package:frontend/presentation/theme/colors.dart';
import 'package:frontend/presentation/widgets/departure_row.dart';

class DepartureBoard extends StatelessWidget {
  const DepartureBoard({super.key, required this.now});

  final DateTime now;

  static const _maxRows     = 5;
  static const _rowOpacity  = [1.0, 1.0, 1.0, 0.65, 0.45];

  @override
  Widget build(BuildContext context) {
    final state = context.watch<StopUpdateCubit>().state;

    return Container(
      decoration: BoxDecoration(
        color: TransitColors.surface,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: TransitColors.border),
      ),
      child: switch (state) {
        StopUpdateIdle()       => _placeholder('Sélectionnez une ligne via la recherche'),
        StopUpdateConnecting() => _placeholder('Connexion en cours…', loading: true),
        StopUpdateError(:final message) => _placeholder('Erreur : $message', error: true),
        StopUpdateLive(:final departures) => departures.isEmpty
            ? _placeholder('Aucun départ planifié')
            : _rows(departures),
      },
    );
  }

  Widget _rows(List<dynamic> departures) {
    final count = departures.length.clamp(0, _maxRows);
    return Column(
      children: List.generate(count, (i) => DepartureRow(
        rank:        i + 1,
        departure:   departures[i],
        now:         now,
        opacity:     i < _rowOpacity.length ? _rowOpacity[i] : 0.35,
        showDivider: i < count - 1,
      )),
    );
  }

  static Widget _placeholder(String msg, {bool loading = false, bool error = false}) {
    return SizedBox(
      height: 200,
      child: Center(
        child: loading
            ? const SizedBox(
                width: 22, height: 22,
                child: CircularProgressIndicator(
                  color: TransitColors.accent,
                  strokeWidth: 1.8,
                ),
              )
            : Text(
                msg,
                style: TextStyle(
                  color: error ? TransitColors.bad : TransitColors.textMuted,
                  fontSize: 11,
                  fontStyle: FontStyle.italic,
                ),
              ),
      ),
    );
  }
}
