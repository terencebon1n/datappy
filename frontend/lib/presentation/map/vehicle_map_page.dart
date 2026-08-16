import 'dart:math' as math;

import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:latlong2/latlong.dart';

import 'package:frontend/application/route_selection/cubit.dart';
import 'package:frontend/application/vehicle_map/cubit.dart';
import 'package:frontend/application/vehicle_map/state.dart';
import 'package:frontend/domain/conveyance.dart';
import 'package:frontend/domain/route_geometry.dart';
import 'package:frontend/domain/vehicle_position.dart';
import 'package:frontend/presentation/theme/colors.dart';

const _fallbackCenter = LatLng(43.6108, 3.8767);
const _tileUrl = 'https://tile.openstreetmap.org/{z}/{x}/{y}.png';
const _userAgent = 'fr.datappy.app';

LatLngBounds? boundsFor(RouteGeometry? geometry) {
  final points = <LatLng>[
    for (final shape in geometry?.shapes ?? const <RouteShape>[])
      for (final point in shape.points) LatLng(point.latitude, point.longitude),
  ];
  if (points.isEmpty) return null;
  return LatLngBounds.fromPoints(points);
}

class VehicleMapPage extends StatelessWidget {
  const VehicleMapPage({super.key});

  @override
  Widget build(BuildContext context) {
    final line = context.select(
      (RouteSelectionCubit c) => c.state.selectedConveyance,
    );
    final state = context.watch<VehicleMapCubit>().state;

    return Column(
      children: [
        _MapHeader(line: line, vehicleCount: state.vehicles.length),
        Expanded(child: _MapBody(state: state, line: line)),
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
      padding: const EdgeInsets.fromLTRB(16, 12, 16, 12),
      color: TransitColors.surface,
      child: Row(
        children: [
          Icon(Icons.map_rounded, size: 18, color: TransitColors.accent),
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
          Text(
            vehicleCount == 1 ? '1 véhicule' : '$vehicleCount véhicules',
            style: TextStyle(fontSize: 12, color: TransitColors.textSecondary),
          ),
        ],
      ),
    );
  }
}

class _MapBody extends StatelessWidget {
  const _MapBody({required this.state, required this.line});

  final VehicleMapState state;
  final Conveyance? line;

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
    final routeColor = Color(line!.colorValue);

    return FlutterMap(
      options: MapOptions(
        initialCenter: _fallbackCenter,
        initialZoom: 12,
        initialCameraFit: bounds == null
            ? null
            : CameraFit.bounds(
                bounds: bounds,
                padding: const EdgeInsets.all(32),
              ),
      ),
      children: [
        TileLayer(urlTemplate: _tileUrl, userAgentPackageName: _userAgent),
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
              ),
          ],
        ),
        MarkerLayer(
          markers: [
            for (final stop in state.geometry?.stops ?? const <RouteStop>[])
              Marker(
                point: LatLng(stop.latitude, stop.longitude),
                width: 10,
                height: 10,
                child: const _StopDot(),
              ),
          ],
        ),
        MarkerLayer(
          markers: [
            for (final vehicle in state.vehicles)
              Marker(
                point: LatLng(vehicle.latitude, vehicle.longitude),
                width: 30,
                height: 30,
                child: _VehicleMarker(vehicle: vehicle, color: routeColor),
              ),
          ],
        ),
        const _Attribution(),
      ],
    );
  }
}

class _StopDot extends StatelessWidget {
  const _StopDot();

  @override
  Widget build(BuildContext context) => DecoratedBox(
        decoration: BoxDecoration(
          shape: BoxShape.circle,
          color: TransitColors.surface,
          border: Border.all(color: TransitColors.textMuted, width: 2),
        ),
      );
}

class _VehicleMarker extends StatelessWidget {
  const _VehicleMarker({required this.vehicle, required this.color});

  final VehiclePosition vehicle;
  final Color color;

  @override
  Widget build(BuildContext context) {
    return Transform.rotate(
      angle: vehicle.bearing * math.pi / 180,
      child: Container(
        decoration: BoxDecoration(
          shape: BoxShape.circle,
          color: color,
          border: Border.all(color: Colors.white, width: 2),
        ),
        child: const Icon(Icons.navigation_rounded, size: 16, color: Colors.white),
      ),
    );
  }
}

class _Attribution extends StatelessWidget {
  const _Attribution();

  @override
  Widget build(BuildContext context) => const RichAttributionWidget(
        attributions: [
          TextSourceAttribution('OpenStreetMap contributors'),
        ],
      );
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
            Icon(icon, size: 32, color: TransitColors.textMuted),
            const SizedBox(height: 12),
            Text(
              text,
              textAlign: TextAlign.center,
              style: TextStyle(fontSize: 13, color: TransitColors.textSecondary),
            ),
          ],
        ),
      ),
    );
  }
}
