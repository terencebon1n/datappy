import 'package:flutter_bloc/flutter_bloc.dart';

import 'package:frontend/domain/city.dart' show City;
import 'package:frontend/domain/repositories/i_stop_departure.dart'
    show IStopDepartureRepository;
import 'state.dart';


class StopDeparturesCubit extends Cubit<StopDeparturesState> {
    final IStopDepartureRepository _repo;

    StopDeparturesCubit({required IStopDepartureRepository repo})
        : _repo = repo,
          super(const StopDeparturesState());

    Future<void> load({required String stopId, required City city}) async {
        emit(const StopDeparturesState(status: StopDeparturesStatus.loading));

        try {
            final departures = await _repo.resolveStopDepartures(
                stopId: stopId,
                city: city,
            );
            emit(StopDeparturesState(
                status: StopDeparturesStatus.ready,
                departures: departures,
            ));
        } catch (_) {
            emit(const StopDeparturesState(status: StopDeparturesStatus.error));
        }
    }
}
