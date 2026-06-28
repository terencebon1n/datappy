import 'package:frontend/domain/city.dart';
import 'package:frontend/domain/conveyance.dart';
import 'package:frontend/domain/direction.dart';

enum RouteSelectionStatus { loading, ready }

enum FunnelStep { city, line, source, dest }

class RouteSelectionState {
  final RouteSelectionStatus status;
  final FunnelStep step;
  final List<City> cities;
  final List<Conveyance> conveyances;
  final List<String> stops;
  final City? selectedCity;
  final Conveyance? selectedConveyance;
  final String? sourceStop;
  final String? destStop;
  final Direction? direction;

  bool get canSubmit =>
      selectedCity != null &&
      selectedConveyance != null &&
      sourceStop != null &&
      destStop != null &&
      sourceStop != destStop &&
      direction != null;

  const RouteSelectionState({
    this.status = RouteSelectionStatus.loading,
    this.step = FunnelStep.city,
    this.cities = const [],
    this.conveyances = const [],
    this.stops = const [],
    this.selectedCity,
    this.selectedConveyance,
    this.sourceStop,
    this.destStop,
    this.direction,
  });

  RouteSelectionState copyWith({
    RouteSelectionStatus? status,
    FunnelStep? step,
    List<City>? cities,
    List<Conveyance>? conveyances,
    List<String>? stops,
    City? selectedCity,
    Conveyance? selectedConveyance,
    String? sourceStop,
    String? destStop,
    Direction? direction,
  }) =>
      RouteSelectionState(
        status: status ?? this.status,
        step: step ?? this.step,
        cities: cities ?? this.cities,
        conveyances: conveyances ?? this.conveyances,
        stops: stops ?? this.stops,
        selectedCity: selectedCity ?? this.selectedCity,
        selectedConveyance: selectedConveyance ?? this.selectedConveyance,
        sourceStop: sourceStop ?? this.sourceStop,
        destStop: destStop ?? this.destStop,
        direction: direction ?? this.direction,
      );
}
