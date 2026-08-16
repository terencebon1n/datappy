import 'package:frontend/domain/stop_departure.dart' show StopDeparture;

enum StopDeparturesStatus { loading, ready, error }

class StopDeparturesState {
    final StopDeparturesStatus status;
    final List<StopDeparture> departures;

    const StopDeparturesState({
        this.status = StopDeparturesStatus.loading,
        this.departures = const [],
    });
}
