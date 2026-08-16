import 'dart:math' as math;

import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:latlong2/latlong.dart';

import 'package:frontend/application/route_selection/cubit.dart';
import 'package:frontend/application/stop_departures/cubit.dart';
import 'package:frontend/application/theme/cubit.dart';
import 'package:frontend/application/vehicle_map/cubit.dart';
import 'package:frontend/application/vehicle_map/state.dart';
import 'package:frontend/domain/conveyance.dart';
import 'package:frontend/domain/route_geometry.dart';
import 'package:frontend/domain/vehicle_position.dart';
import 'package:frontend/presentation/map/stop_details_sheet.dart';
import 'package:frontend/presentation/map/vehicle_details_sheet.dart';
import 'package:frontend/presentation/theme/colors.dart';

const _fallbackCenter = LatLng(43.6108, 3.8767);
const _userAgent = 'fr.datappy.app';

const _lightBasemap =
    'https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png';
const _darkBasemap =
    'https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png';

String basemapUrl({required bool isDark}) => isDark ? _darkBasemap : _lightBasemap;

LatLngBounds? boundsFor(RouteGeometry? geometry) {
  final points = <LatLng>[
    for (final shape in geometry?.shapes ?? const <RouteShape>[])
      for (final point in shape.points) LatLng(point.latitude, point.longitude),
  ];
  if (points.isEmpty) return null;
  return LatLngBounds.fromPoints(points);
}

Color readableRouteColor(Conveyance line, {required bool isDark}) {
  final color = Color(line.colorValue);
  final luminance = color.computeLuminance();
  if (isDark && luminance < 0.18) return TransitColors.accent;
  if (!isDark && luminance > 0.82) return TransitColors.accent;
  return color;
}

class VehicleMapPage extends StatelessWidget {
  const VehicleMapPage({super.key});

  @override
  Widget build(BuildContext context) {
    final line = context.select(
      (RouteSelectionCubit c) => c.state.selectedConveyance,
    );
    final state = context.watch<VehicleMapCubit>().state;
    final isDark = resolveIsDark(context.watch<ThemeCubit>().state);

    return Column(
      children: [
        _MapHeader(line: line, vehicleCount: state.vehicles.length),
        Expanded(
          child: ColoredBox(
            color: TransitColors.bg,
            child: _MapBody(state: state, line: line, isDark: isDark),
          ),
        ),
      ],
    );
  }
}

class _MapHeader extends StatelessWidget {
  const _MapHeader({required this.line, required this.vehicleCount});

  final Conveyance? line;
  final int vehicleCount;

  @override
  Widget build(BuildContext context) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.fromLTRB(14, 12, 14, 12),
      decoration: BoxDecoration(
        color: TransitColors.surface,
        border: Border(bottom: BorderSide(color: TransitColors.border)),
      ),
      child: Row(
        children: [
          Container(
            width: 30,
            height: 30,
            decoration: BoxDecoration(
              color: TransitColors.accentBg,
              borderRadius: BorderRadius.circular(10),
              border: Border.all(color: TransitColors.accentBorder),
            ),
            child: Icon(Icons.map_rounded, size: 16, color: TransitColors.accent),
          ),
          const SizedBox(width: 10),
          Expanded(
            child: Text(
              line == null ? 'Carte' : 'Ligne ${line!.shortName}',
              maxLines: 1,
              overflow: TextOverflow.ellipsis,
              style: TextStyle(
                fontSize: 15,
                fontWeight: FontWeight.w600,
                color: TransitColors.textPrimary,
              ),
            ),
          ),
          if (line != null) _VehicleCount(count: vehicleCount),
        ],
      ),
    );
  }
}

class _VehicleCount extends StatelessWidget {
  const _VehicleCount({required this.count});

  final int count;

  @override
  Widget build(BuildContext context) {
    final live = count > 0;

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 9, vertical: 5),
      decoration: BoxDecoration(
        color: live ? TransitColors.liveBg : TransitColors.surfaceHigh,
        borderRadius: BorderRadius.circular(999),
        border: Border.all(
          color: live ? TransitColors.liveBorder : TransitColors.border,
        ),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Container(
            width: 6,
            height: 6,
            decoration: BoxDecoration(
              shape: BoxShape.circle,
              color: live ? TransitColors.live : TransitColors.textMuted,
            ),
          ),
          const SizedBox(width: 6),
          Text(
            count == 1 ? '1 véhicule' : '$count véhicules',
            style: TextStyle(
              fontSize: 11,
              fontWeight: FontWeight.w600,
              color: live ? TransitColors.live : TransitColors.textSecondary,
            ),
          ),
        ],
      ),
    );
  }
}

class _MapBody extends StatelessWidget {
  const _MapBody({
    required this.state,
    required this.line,
    required this.isDark,
  });

  final VehicleMapState state;
  final Conveyance? line;
  final bool isDark;

  @override
  Widget build(BuildContext context) {
    if (line == null) {
      return const _Notice(
        icon: Icons.search_rounded,
        text: 'Choisissez une ligne pour suivre ses véhicules en direct.',
      );
    }

    if (state.status == VehicleMapStatus.loading) {
      return Center(child: CircularProgressIndicator(color: TransitColors.accent));
    }

    if (state.status == VehicleMapStatus.error) {
      return const _Notice(
        icon: Icons.cloud_off_rounded,
        text: 'Impossible de charger la carte en direct.',
      );
    }

    final bounds = boundsFor(state.geometry);
    final routeColor = readableRouteColor(line!, isDark: isDark);

    return FlutterMap(
      options: MapOptions(
        backgroundColor: TransitColors.bg,
        initialCenter: _fallbackCenter,
        initialZoom: 12,
        initialCameraFit: bounds == null
            ? null
            : CameraFit.bounds(
                bounds: bounds,
                padding: const EdgeInsets.all(36),
              ),
      ),
      children: [
        TileLayer(
          urlTemplate: basemapUrl(isDark: isDark),
          subdomains: const ['a', 'b', 'c', 'd'],
          retinaMode: RetinaMode.isHighDensity(context),
          userAgentPackageName: _userAgent,
        ),
        PolylineLayer(
          polylines: [
            for (final shape in state.geometry?.shapes ?? const <RouteShape>[])
              Polyline(
                points: [
                  for (final point in shape.points)
                    LatLng(point.latitude, point.longitude),
                ],
                color: routeColor,
                strokeWidth: 4,
                borderColor: TransitColors.surface,
                borderStrokeWidth: 2,
              ),
          ],
        ),
        MarkerLayer(
          markers: [
            for (final stop in state.geometry?.stops ?? const <RouteStop>[])
              Marker(
                point: LatLng(stop.latitude, stop.longitude),
                width: 26,
                height: 26,
                child: GestureDetector(
                  behavior: HitTestBehavior.opaque,
                  onTap: () => openStopDetails(context, stop, routeColor),
                  child: Center(
                    child: SizedBox(
                      width: 9,
                      height: 9,
                      child: _StopDot(routeColor: routeColor),
                    ),
                  ),
                ),
              ),
          ],
        ),
        MarkerLayer(
          markers: [
            for (final vehicle in state.vehicles)
              Marker(
                point: LatLng(vehicle.latitude, vehicle.longitude),
                width: 34,
                height: 34,
                child: GestureDetector(
                  behavior: HitTestBehavior.opaque,
                  onTap: () => openVehicleDetails(
                    context,
                    vehicle,
                    routeColor,
                    state.geometry?.headsignFor(vehicle.directionId),
                  ),
                  child: Center(
                    child: SizedBox(
                      width: 28,
                      height: 28,
                      child: _VehicleMarker(vehicle: vehicle, color: routeColor),
                    ),
                  ),
                ),
              ),
          ],
        ),
        const _Attribution(),
      ],
    );
  }
}

Future<void> openStopDetails(
  BuildContext context,
  RouteStop stop,
  Color routeColor,
) {
  final selection = context.read<RouteSelectionCubit>().state;
  final departures = context.read<StopDeparturesCubit>();

  if (selection.selectedCity != null) {
    departures.load(stopId: stop.id, city: selection.selectedCity!);
  }

  return showModalBottomSheet<void>(
    context: context,
    backgroundColor: Colors.transparent,
    builder: (_) => BlocProvider.value(
      value: departures,
      child: StopDetailsSheet(
        stop: stop,
        routeColor: routeColor,
        now: DateTime.now(),
      ),
    ),
  );
}

Future<void> openVehicleDetails(
  BuildContext context,
  VehiclePosition vehicle,
  Color routeColor,
  String? headsign,
) {
  return showModalBottomSheet<void>(
    context: context,
    backgroundColor: Colors.transparent,
    builder: (_) => VehicleDetailsSheet(
      vehicle: vehicle,
      routeColor: routeColor,
      headsign: headsign,
      now: DateTime.now(),
    ),
  );
}

class _StopDot extends StatelessWidget {
  const _StopDot({required this.routeColor});

  final Color routeColor;

  @override
  Widget build(BuildContext context) => DecoratedBox(
        decoration: BoxDecoration(
          shape: BoxShape.circle,
          color: TransitColors.surface,
          border: Border.all(color: routeColor, width: 2),
        ),
      );
}

class _VehicleMarker extends StatelessWidget {
  const _VehicleMarker({required this.vehicle, required this.color});

  final VehiclePosition vehicle;
  final Color color;

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: BoxDecoration(
        shape: BoxShape.circle,
        color: color,
        border: Border.all(color: TransitColors.surface, width: 2.5),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withValues(alpha: 0.25),
            blurRadius: 4,
            offset: const Offset(0, 1),
          ),
        ],
      ),
      child: Transform.rotate(
        angle: vehicle.bearing * math.pi / 180,
        child: Icon(
          Icons.navigation_rounded,
          size: 14,
          color: TransitColors.surface,
        ),
      ),
    );
  }
}

class _Attribution extends StatelessWidget {
  const _Attribution();

  @override
  Widget build(BuildContext context) {
    return Align(
      alignment: Alignment.bottomRight,
      child: Padding(
        padding: const EdgeInsets.fromLTRB(0, 0, 6, 6),
        child: DecoratedBox(
          decoration: BoxDecoration(
            color: TransitColors.surface.withValues(alpha: 0.82),
            borderRadius: BorderRadius.circular(6),
            border: Border.all(color: TransitColors.border),
          ),
          child: Padding(
            padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 3),
            child: Text(
              '© OpenStreetMap · © CARTO',
              style: TextStyle(fontSize: 9, color: TransitColors.textMuted),
            ),
          ),
        ),
      ),
    );
  }
}

class _Notice extends StatelessWidget {
  const _Notice({required this.icon, required this.text});

  final IconData icon;
  final String text;

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 32),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Container(
              width: 48,
              height: 48,
              decoration: BoxDecoration(
                color: TransitColors.surfaceHigh,
                shape: BoxShape.circle,
                border: Border.all(color: TransitColors.border),
              ),
              child: Icon(icon, size: 22, color: TransitColors.textMuted),
            ),
            const SizedBox(height: 14),
            Text(
              text,
              textAlign: TextAlign.center,
              style: TextStyle(
                fontSize: 13,
                height: 1.4,
                color: TransitColors.textSecondary,
              ),
            ),
          ],
        ),
      ),
    );
  }
}
