import 'dart:async';
import 'dart:io';

import 'package:flutter_test/flutter_test.dart';

import 'package:frontend/application/stop_update/cubit.dart';
import 'package:frontend/application/stop_update/state.dart';
import 'package:frontend/domain/direction.dart';
import 'package:frontend/domain/transit_path.dart';
import 'package:frontend/domain/saved_selection.dart';
import 'package:frontend/domain/repositories/i_selection_store.dart';
import 'package:frontend/infrastructure/backend/repositories/stop_update.dart';

class _NullStore implements ISelectionStore {
  @override
  Future<SavedSelection?> load() async => null;
  @override
  Future<void> save(SavedSelection s) async {}
}

TransitPath _path() => TransitPath(
      city: 'lyon',
      routeId: 'T1',
      direction: Direction(directionId: 0, stopIdOrigin: 'o', stopIdDestination: 'd'),
    );

List<WebSocket> _serve(HttpServer server) {
  final sockets = <WebSocket>[];
  server.listen((req) async {
    if (WebSocketTransformer.isUpgradeRequest(req)) {
      final ws = await WebSocketTransformer.upgrade(req);
      sockets.add(ws);
      ws.add('[]'); // valid empty payload -> StopUpdateLive([])
    } else {
      req.response.statusCode = HttpStatus.badRequest;
      await req.response.close();
    }
  });
  return sockets;
}

Future<HttpServer> _bind(int port) async {
  for (var i = 0; i < 50; i++) {
    try {
      return await HttpServer.bind(InternetAddress.loopbackIPv4, port);
    } catch (_) {
      await Future<void>.delayed(const Duration(milliseconds: 100));
    }
  }
  throw StateError('could not bind port $port');
}

Future<void> _waitFor(
  bool Function() cond, {
  Duration timeout = const Duration(seconds: 15),
  String? reason,
}) async {
  final deadline = DateTime.now().add(timeout);
  while (!cond()) {
    if (DateTime.now().isAfter(deadline)) {
      throw TimeoutException(reason ?? 'condition not met within $timeout');
    }
    await Future<void>.delayed(const Duration(milliseconds: 50));
  }
}

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  test('reconnects after the websocket server restarts (real sockets)', () async {
    var server = await _bind(0);
    final port = server.port;
    var sockets = _serve(server);

    final repo = StopUpdateRepository(wsBase: 'ws://127.0.0.1:$port');
    final cubit = StopUpdateCubit(stopUpdateRepo: repo, selectionStore: _NullStore());

    cubit.watchStopUpdates(_path());
    await _waitFor(() => cubit.state is StopUpdateLive,
        reason: 'initial connection should go live');

    // Simulate the backend restarting: kill the live connection (like the OS
    // closing sockets when the process dies), then bring the server back up.
    for (final ws in sockets) {
      await ws.close();
    }
    await server.close(force: true);
    await _waitFor(() => cubit.state is! StopUpdateLive,
        timeout: const Duration(seconds: 10),
        reason: 'a severed connection must be noticed promptly');

    server = await _bind(port);
    sockets = _serve(server);

    await _waitFor(() => cubit.state is StopUpdateLive,
        timeout: const Duration(seconds: 40),
        reason: 'cubit must reconnect on its own after the server is back');

    await cubit.close();
    await server.close(force: true);
  }, timeout: const Timeout(Duration(seconds: 120)));

  test('connects once the server appears (backend down then up)', () async {
    // Reserve a port, then free it so nothing is listening: the first connect
    // attempts must hit "connection refused", exactly like a backend mid-restart.
    final probe = await _bind(0);
    final port = probe.port;
    await probe.close(force: true);

    final repo = StopUpdateRepository(wsBase: 'ws://127.0.0.1:$port');
    final cubit = StopUpdateCubit(stopUpdateRepo: repo, selectionStore: _NullStore());

    cubit.watchStopUpdates(_path());

    // Let several reconnect attempts hit the closed port.
    await Future<void>.delayed(const Duration(seconds: 4));
    expect(cubit.state, isNot(isA<StopUpdateLive>()));

    final server = await _bind(port);
    _serve(server);

    await _waitFor(() => cubit.state is StopUpdateLive,
        timeout: const Duration(seconds: 20),
        reason: 'cubit must connect once the server is back up');

    await cubit.close();
    await server.close(force: true);
  }, timeout: const Timeout(Duration(seconds: 60)));
}
