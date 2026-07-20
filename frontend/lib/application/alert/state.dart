import 'package:frontend/domain/alert.dart';


sealed class AlertState {
  const AlertState();
}


class AlertIdle extends AlertState {
  const AlertIdle();
}


class AlertLoading extends AlertState {
  const AlertLoading();
}


class AlertLoaded extends AlertState {
  final List<Alert> alerts;
  const AlertLoaded(this.alerts);
}


class AlertError extends AlertState {
  final String message;
  const AlertError(this.message);
}
