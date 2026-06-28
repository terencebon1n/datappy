import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_bloc/flutter_bloc.dart';

import 'package:frontend/application/route_selection/cubit.dart';
import 'package:frontend/application/route_selection/state.dart';
import 'package:frontend/application/stop_update/cubit.dart';
import 'package:frontend/domain/transit_path.dart';
import 'package:frontend/presentation/funnel/funnel_colors.dart';
import 'package:frontend/presentation/funnel/city_step.dart';
import 'package:frontend/presentation/funnel/line_step.dart';
import 'package:frontend/presentation/funnel/stop_step.dart';

class FunnelPage extends StatelessWidget {
  const FunnelPage({super.key});

  @override
  Widget build(BuildContext context) {
    return AnnotatedRegion<SystemUiOverlayStyle>(
      value: const SystemUiOverlayStyle(
        statusBarColor: Colors.transparent,
        statusBarIconBrightness: Brightness.light,
        statusBarBrightness: Brightness.dark,
      ),
      child: BlocListener<RouteSelectionCubit, RouteSelectionState>(
        listenWhen: (prev, curr) => !prev.canSubmit && curr.canSubmit,
        listener: (context, state) {
          if (!(ModalRoute.of(context)?.isCurrent ?? false)) return;
          context.read<StopUpdateCubit>().watchStopUpdates(
            TransitPath(
              city: state.selectedCity!.name.toLowerCase(),
              routeId: state.selectedConveyance!.id,
              direction: state.direction!,
            ),
          );
          Navigator.of(context).pop(true);
        },
        child: Builder(
          builder: (context) {
            final step = context.select(
              (RouteSelectionCubit c) => c.state.step,
            );
            return PopScope(
              canPop: step == FunnelStep.city,
              onPopInvokedWithResult: (didPop, _) {
                if (!didPop) context.read<RouteSelectionCubit>().back();
              },
              child: Scaffold(
                backgroundColor: FunnelColors.surface,
                body: SafeArea(
                  top: false,
                  child: switch (step) {
                    FunnelStep.city => const CityStep(),
                    FunnelStep.line => const LineStep(),
                    FunnelStep.source => const StopStep(
                      key: ValueKey('source'),
                      isSource: true,
                    ),
                    FunnelStep.dest => const StopStep(
                      key: ValueKey('dest'),
                      isSource: false,
                    ),
                  },
                ),
              ),
            );
          },
        ),
      ),
    );
  }
}
