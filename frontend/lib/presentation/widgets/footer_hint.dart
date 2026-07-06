import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';

import 'package:frontend/application/stop_update/cubit.dart';
import 'package:frontend/application/stop_update/state.dart';
import 'package:frontend/presentation/theme/colors.dart';

class FooterHint extends StatelessWidget {
  const FooterHint({super.key});

  @override
  Widget build(BuildContext context) {
    final state = context.watch<StopUpdateCubit>().state;
    if (state is! StopUpdateLive) return const SizedBox.shrink();

    return Padding(
      padding: const EdgeInsets.only(top: 6),
      child: Text(
        'Mis à jour à la seconde · GTFS Realtime',
        textAlign: TextAlign.center,
        style: TextStyle(
          fontSize: 8.5,
          color: TransitColors.textMuted,
          letterSpacing: 0.4,
        ),
      ),
    );
  }
}
