import 'package:frontend/domain/stop_update.dart';


sealed class StopUpdateState {
  const StopUpdateState();
}


class StopUpdateIdle extends StopUpdateState {
  const StopUpdateIdle();
}


class StopUpdateConnecting extends StopUpdateState {
  const StopUpdateConnecting();
}


class StopUpdateLive extends StopUpdateState {
  final List<StopUpdate> departures;
  const StopUpdateLive(this.departures);
}


class StopUpdateError extends StopUpdateState {
  final String message;
  const StopUpdateError(this.message);
}
