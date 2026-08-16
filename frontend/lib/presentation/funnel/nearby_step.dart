import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';

import 'package:frontend/application/nearby/cubit.dart';
import 'package:frontend/application/nearby/state.dart';
import 'package:frontend/application/route_selection/cubit.dart';
import 'package:frontend/application/route_selection/state.dart';
import 'package:frontend/domain/nearby_stop.dart';
import 'package:frontend/presentation/funnel/funnel_colors.dart';
import 'package:frontend/presentation/funnel/funnel_header.dart';
import 'package:frontend/presentation/funnel/funnel_widgets.dart';

String formatDistance(int meters) =>
    meters < 1000 ? '$meters m' : '${(meters / 1000).toStringAsFixed(1)} km';

class NearbyStep extends StatelessWidget {
  const NearbyStep({super.key});

  @override
  Widget build(BuildContext context) {
    final cubit = context.read<RouteSelectionCubit>();
    final city = context.select((RouteSelectionCubit c) => c.state.selectedCity);
    final state = context.watch<NearbyCubit>().state;

    return Column(
      children: [
        FunnelHeader(
          overline: city?.name ?? '',
          title: 'Autour de moi',
          stepperFor: FunnelStep.nearby,
          onLeading: cubit.back,
        ),
        Expanded(child: _Body(state: state)),
      ],
    );
  }
}

class _Body extends StatelessWidget {
  const _Body({required this.state});

  final NearbyState state;

  @override
  Widget build(BuildContext context) {
    if (state.isBusy) {
      return _Centered(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            CircularProgressIndicator(color: FunnelColors.header),
            const SizedBox(height: 12),
            Text(
              state.status == NearbyStatus.locating
                  ? 'Localisation en cours…'
                  : 'Recherche des arrêts…',
              style: TextStyle(fontSize: 13, color: FunnelColors.textSecondary),
            ),
          ],
        ),
      );
    }

    final message = switch (state.status) {
      NearbyStatus.denied =>
        'Datappy a besoin de votre position pour trouver les arrêts proches. '
            'Autorisez la localisation dans les réglages.',
      NearbyStatus.serviceDisabled =>
        'La localisation est désactivée sur cet appareil. Activez-la puis réessayez.',
      NearbyStatus.failed => 'Impossible de récupérer les arrêts proches.',
      _ => null,
    };

    if (message != null) {
      return _Centered(child: _Message(text: message));
    }

    if (state.stops.isEmpty) {
      return _Centered(
        child: _Message(text: 'Aucun arrêt à proximité.'),
      );
    }

    return ListView(
      padding: const EdgeInsets.only(bottom: 16),
      children: [
        const FunnelSectionLabel('Arrêts les plus proches'),
        for (final stop in state.stops) _NearbyStopCard(stop: stop),
      ],
    );
  }
}

class _Centered extends StatelessWidget {
  const _Centered({required this.child});

  final Widget child;

  @override
  Widget build(BuildContext context) => Center(
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 32),
          child: child,
        ),
      );
}

class _Message extends StatelessWidget {
  const _Message({required this.text});

  final String text;

  @override
  Widget build(BuildContext context) => Text(
        text,
        textAlign: TextAlign.center,
        style: TextStyle(fontSize: 13, color: FunnelColors.textSecondary),
      );
}

class _NearbyStopCard extends StatelessWidget {
  const _NearbyStopCard({required this.stop});

  final NearbyStop stop;

  @override
  Widget build(BuildContext context) {
    final cubit = context.read<RouteSelectionCubit>();

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Container(
          width: double.infinity,
          color: FunnelColors.surfaceMuted,
          padding: const EdgeInsets.fromLTRB(16, 10, 16, 10),
          child: Row(
            children: [
              const Icon(Icons.near_me, size: 15, color: FunnelColors.tramAccent),
              const SizedBox(width: 10),
              Expanded(
                child: Text(
                  stop.name,
                  maxLines: 2,
                  overflow: TextOverflow.ellipsis,
                  style: TextStyle(
                    fontSize: 14,
                    fontWeight: FontWeight.w600,
                    color: FunnelColors.textPrimary,
                  ),
                ),
              ),
              Text(
                formatDistance(stop.distanceMeters),
                style: TextStyle(fontSize: 12, color: FunnelColors.textSecondary),
              ),
            ],
          ),
        ),
        for (final route in stop.routes)
          RouteListTile(
            conveyance: route,
            onTap: () => cubit.selectNearbyStop(stop, route),
          ),
      ],
    );
  }
}
