import 'dart:async';
import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;

import 'models.dart';

import 'package:frontend/domain/conveyance.dart' show Conveyance;
import 'package:frontend/domain/direction.dart' show Direction;
import 'package:frontend/domain/path.dart' show Path;
import 'package:frontend/domain/route_type.dart' show RouteType;
import 'package:frontend/domain/stop_update.dart' show StopUpdate;
import 'package:frontend/domain/transit_path.dart' show TransitPath;
import 'package:frontend/infrastructure/backend/repositories/conveyance.dart' show ConveyanceRepository;
import 'package:frontend/infrastructure/backend/repositories/direction.dart' show DirectionRepository;
import 'package:frontend/infrastructure/backend/repositories/route_type.dart' show RouteTypeRepository;
import 'package:frontend/infrastructure/backend/repositories/stop_name.dart' show StopNameRepository;
import 'package:frontend/infrastructure/backend/repositories/stop_update.dart' show StopUpdateRepository;


void main() {
  runApp(const MaterialApp(
    debugShowCheckedModeBanner: false,
    home: TransitDashboard(),
  ));
}

class TransitDashboard extends StatefulWidget {
  const TransitDashboard({super.key});

  @override
  State<TransitDashboard> createState() => _TransitDashboardState();
}

class _TransitDashboardState extends State<TransitDashboard> {
  // Configuration
  final String apiBase = "http://localhost:8000";
  final String wsBase = "ws://localhost:8000";
  final Map<String, String> headers = {'City': 'montpellier'};

  // State Data
  List<RouteType> routeTypes = [];
  List<Conveyance> conveyances = [];
  List<String> stops = [];
  List<StopUpdate> updates = [];

  // Selections
  RouteType? selectedType;
  Conveyance? selectedConveyance;
  String? sourceStop;
  String? destStop;

  ConveyanceRepository? conveyanceRepository;
  RouteTypeRepository? routeTypeRepository;
  DirectionRepository? directionRepository;
  StopNameRepository? stopNameRepository;
  StopUpdateRepository? stopUpdateRepository;

  // Stream/Socket
  StreamSubscription<List<StopUpdate>>? _channel;
  bool isConnecting = false;

    @override
    void initState() {
        super.initState();
        conveyanceRepository = ConveyanceRepository(apiBase: apiBase, headers: headers);
        directionRepository = DirectionRepository(apiBase: apiBase, headers: headers);
        routeTypeRepository = RouteTypeRepository(apiBase: apiBase, headers: headers);
        stopNameRepository = StopNameRepository(apiBase: apiBase, headers: headers);
        stopUpdateRepository = StopUpdateRepository(wsBase: wsBase);
        routeTypeRepository!.resolveRouteTypes().then((rt) => setState(() => routeTypes = rt));
    }

  // --- API Methods ---
  void _startStreaming() async {
    setState(() {
      isConnecting = true;
      updates = [];
    });
    
    if (_channel != null) _channel!.cancel();

    try {
      final dirRepo = DirectionRepository(
        apiBase: apiBase,
        headers: headers,
      );

      final path = Path(
        routeId: selectedConveyance!.id,
        stopNameOrigin: sourceStop!,
        stopNameDestination: destStop!,
      );

      final Direction dirData = await dirRepo.resolveDirection(path);

      final stopUpdateRepo = StopUpdateRepository(wsBase: wsBase);

      final transitPath = TransitPath(
        city: "montpellier",
        routeId: selectedConveyance!.id,
        direction: dirData,
      );


      _channel = stopUpdateRepo.watchStopUpdates(transitPath).listen((updates) {
        setState(() {
          this.updates = updates;
          isConnecting = false;
        });
      }, onError: (err) {
        setState(() => isConnecting = false);
        debugPrint(updates.toString());
        debugPrint("Stream Error: $err");
      });
    } catch (e) {
      setState(() => isConnecting = false);
      debugPrint("Stream Error: $e");
    }
  }


  // --- Helper for Time Formatting ---
  String _formatTimestamp(int? ts) {
    if (ts == null) return "--:--";
    final dt = DateTime.fromMillisecondsSinceEpoch(ts * 1000);
    return "${dt.hour.toString().padLeft(2, '0')}:${dt.minute.toString().padLeft(2, '0')}";
  }

  @override
  void dispose() {
    _channel?.cancel();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
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
              value: selectedType,
              items: routeTypes.map((t) => DropdownMenuItem(value: t, child: Text(t.name))).toList(),
              onChanged: (val) {
                setState(() {
                  selectedType = val;
                  selectedConveyance = null;
                  conveyances = [];
                });
                if (val != null) {
                    conveyanceRepository!.resolveConveyances(val)
                    .then((c) => setState(() => conveyances = c));
                }
              },
              decoration: const InputDecoration(filled: true, fillColor: Colors.white, border: OutlineInputBorder()),
            ),
            const SizedBox(height: 16),

            // 2. Conveyance
            _buildLabel("2. Route (Conveyance)"),
            DropdownButtonFormField<Conveyance>(
              value: selectedConveyance,
              disabledHint: const Text("Select type first"),
              items: conveyances.map((c) => DropdownMenuItem(value: c, child: Text(c.longName))).toList(),
              onChanged: selectedType == null ? null : (val) {
                setState(() {
                  selectedConveyance = val;
                  sourceStop = null;
                  destStop = null;
                  stops = [];
                });
                if (val != null) {
                    stopNameRepository!.resolveStopNames(val.id)
                    .then((s) => setState(() => stops = s));
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
                        value: sourceStop,
                        items: stops.map((s) => DropdownMenuItem(value: s, child: Text(s, overflow: TextOverflow.ellipsis))).toList(),
                        onChanged: selectedConveyance == null ? null : (val) => setState(() => sourceStop = val),
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
                        value: destStop,
                        items: stops.map((s) => DropdownMenuItem(value: s, child: Text(s, overflow: TextOverflow.ellipsis))).toList(),
                        onChanged: selectedConveyance == null ? null : (val) => setState(() => destStop = val),
                        decoration: const InputDecoration(filled: true, fillColor: Colors.white, border: OutlineInputBorder()),
                      ),
                    ],
                  ),
                ),
              ],
            ),
            const SizedBox(height: 24),

            // Action Button
            ElevatedButton(
              onPressed: (sourceStop != null && destStop != null) ? _startStreaming : null,
              style: ElevatedButton.styleFrom(
                backgroundColor: Colors.indigo,
                foregroundColor: Colors.white,
                padding: const EdgeInsets.symmetric(vertical: 16),
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
              ),
              child: isConnecting 
                ? const SizedBox(height: 20, width: 20, child: CircularProgressIndicator(color: Colors.white, strokeWidth: 2))
                : const Text("GET LIVE TRIP UPDATES", style: TextStyle(fontWeight: FontWeight.bold)),
            ),

            const SizedBox(height: 24),

            // Result Terminal
            Container(
              decoration: BoxDecoration(color: Colors.grey[900], borderRadius: BorderRadius.circular(8)),
              padding: const EdgeInsets.all(12),
              constraints: const BoxConstraints(minHeight: 200),
              child: updates.isEmpty
                ? const Center(child: Text("// Results will appear here...", style: TextStyle(color: Colors.grey, fontStyle: FontStyle.italic)))
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
                      ...updates.map((up) => Padding(
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
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildLabel(String text) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 4.0),
      child: Text(text, style: TextStyle(fontSize: 12, fontWeight: FontWeight.w600, color: Colors.grey[700])),
    );
  }
}
