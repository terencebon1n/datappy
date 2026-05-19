import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';

import 'package:frontend/domain/conveyance.dart';
import 'package:frontend/domain/route_type.dart';
import 'package:frontend/domain/transit_path.dart';

import 'package:frontend/application/route_selection/cubit.dart';
import 'package:frontend/application/stop_update/cubit.dart';
import 'package:frontend/application/stop_update/state.dart';

class TransitDashboard extends StatelessWidget {
  const TransitDashboard({super.key});

  String _formatTimestamp(int? ts) {
    if (ts == null) return "--:--";
    final dt = DateTime.fromMillisecondsSinceEpoch(ts * 1000);
    return "${dt.hour.toString().padLeft(2, '0')}:${dt.minute.toString().padLeft(2, '0')}";
  }

  @override
  Widget build(BuildContext context) {
    final selectionState = context.watch<RouteSelectionCubit>().state;
    final updateState = context.watch<StopUpdateCubit>().state;

    return Scaffold(
      backgroundColor: Colors.grey[100],
      appBar: AppBar(
        title: const Text("GTFS Real-Time Viewer", style: TextStyle(fontWeight: FontWeight.bold)),
        backgroundColor: Colors.indigo,
        foregroundColor: Colors.white,
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            // 1. Transport Type
            _buildLabel("1. Transport Type"),
            DropdownButtonFormField<RouteType>(
              value: selectionState.selectedType,
              items: selectionState.routeTypes.map((t) => DropdownMenuItem(value: t, child: Text(t.name))).toList(),
              onChanged: (val) {
                if (val != null) {
                  context.read<RouteSelectionCubit>().selectRouteType(val);
                  context.read<StopUpdateCubit>().stop();
                }
              },
              decoration: const InputDecoration(filled: true, fillColor: Colors.white, border: OutlineInputBorder()),
            ),
            const SizedBox(height: 16),

            // 2. Conveyance
            _buildLabel("2. Route (Conveyance)"),
            DropdownButtonFormField<Conveyance>(
              value: selectionState.selectedConveyance,
              disabledHint: const Text("Select type first"),
              items: selectionState.conveyances.map((c) => DropdownMenuItem(value: c, child: Text(c.longName))).toList(),
              onChanged: selectionState.selectedType == null
                  ? null
                  : (val) {
                      if (val != null) {
                        context.read<RouteSelectionCubit>().selectConveyance(val);
                        context.read<StopUpdateCubit>().stop();
                      }
                    },
              decoration: const InputDecoration(filled: true, fillColor: Colors.white, border: OutlineInputBorder()),
            ),
            const SizedBox(height: 16),

            // 3. Source & Destination
            Row(
              children: [
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      _buildLabel("3. Origin"),
                      DropdownButtonFormField<String>(
                        value: selectionState.sourceStop,
                        items: selectionState.stops.map((s) => DropdownMenuItem(value: s, child: Text(s, overflow: TextOverflow.ellipsis))).toList(),
                        onChanged: selectionState.selectedConveyance == null
                            ? null
                            : (val) => context.read<RouteSelectionCubit>().selectSourceStop(val!),
                        decoration: const InputDecoration(filled: true, fillColor: Colors.white, border: OutlineInputBorder()),
                      ),
                    ],
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      _buildLabel("4. Destination"),
                      DropdownButtonFormField<String>(
                        value: selectionState.destStop,
                        items: selectionState.stops.map((s) => DropdownMenuItem(value: s, child: Text(s, overflow: TextOverflow.ellipsis))).toList(),
                        onChanged: selectionState.selectedConveyance == null
                            ? null
                            : (val) => context.read<RouteSelectionCubit>().selectDestStop(val!),
                        decoration: const InputDecoration(filled: true, fillColor: Colors.white, border: OutlineInputBorder()),
                      ),
                    ],
                  ),
                ),
              ],
            ),
            const SizedBox(height: 24),

            // Action Button — Invoking your exact cubit stream directly inline
            ElevatedButton(
              onPressed: selectionState.canSubmit && updateState is! StopUpdateConnecting
                  ? () {
                      context.read<StopUpdateCubit>().watchStopUpdates(
                        TransitPath(
                          city: "montpellier",
                          routeId: selectionState.selectedConveyance!.id,
                          direction: selectionState.direction!, // Ready directly from state
                        ),
                      );
                    }
                  : null,
              child: updateState is StopUpdateConnecting
                  ? const CircularProgressIndicator()
                  : const Text("GET LIVE TRIP UPDATES"),
            ),
            const SizedBox(height: 24),

            // Result Terminal Content
            Container(
              decoration: BoxDecoration(color: Colors.grey[900], borderRadius: BorderRadius.circular(8)),
              padding: const EdgeInsets.all(12),
              constraints: const BoxConstraints(minHeight: 200),
              child: _buildTerminalContent(updateState),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildTerminalContent(StopUpdateState state) {
    return switch (state) {
      StopUpdateIdle() => const Center(
          child: Text("// Results will appear here...", style: TextStyle(color: Colors.grey, fontStyle: FontStyle.italic)),
        ),
      StopUpdateConnecting() => const Center(
          child: CircularProgressIndicator(color: Colors.indigoAccent),
        ),
      StopUpdateError(:final message) => Center(
          child: Text("Error: $message", style: const TextStyle(color: Colors.redAccent, fontFamily: 'monospace')),
        ),
      StopUpdateLive(:final departures) => departures.isEmpty
          ? const Center(
              child: Text("// Connected. No scheduled departures.", style: TextStyle(color: Colors.grey, fontStyle: FontStyle.italic)),
            )
          : Column(
              children: [
                const Row(
                  children: [
                    Icon(Icons.sensors, color: Colors.green, size: 16),
                    SizedBox(width: 8),
                    Text("LIVE TRACKING ACTIVE", style: TextStyle(color: Colors.green, fontSize: 10, fontWeight: FontWeight.bold, letterSpacing: 1.2)),
                  ],
                ),
                const Divider(color: Colors.grey),
                ...departures.map((up) => Padding(
                      padding: const EdgeInsets.symmetric(vertical: 8.0),
                      child: Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          Text(up.tripId.split('-')[0], style: const TextStyle(color: Colors.white, fontFamily: 'monospace', fontSize: 12)),
                          Text(_formatTimestamp(up.departureTime), style: const TextStyle(color: Colors.indigoAccent, fontWeight: FontWeight.bold)),
                          Text(
                            up.arrivalDelay == 0 ? "On Time" : "${up.arrivalDelay > 0 ? '+' : ''}${up.arrivalDelay ~/ 60}m",
                            style: TextStyle(color: up.arrivalDelay > 0 ? Colors.redAccent : Colors.greenAccent, fontSize: 12),
                          ),
                        ],
                      ),
                    )),
              ],
            ),
    };
  }

  Widget _buildLabel(String text) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 4.0),
      child: Text(text, style: TextStyle(fontSize: 12, fontWeight: FontWeight.w600, color: Colors.grey[700])),
    );
  }
}
