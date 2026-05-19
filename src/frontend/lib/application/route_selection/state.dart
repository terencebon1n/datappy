import 'package:frontend/domain/conveyance.dart';
import 'package:frontend/domain/route_type.dart';
import 'package:frontend/domain/direction.dart';

enum RouteSelectionStatus { loading, ready }

class RouteSelectionState {
  final RouteSelectionStatus status;
  final List<RouteType> routeTypes;
  final List<Conveyance> conveyances;
  final List<String> stops;
  final RouteType? selectedType;
  final Conveyance? selectedConveyance;
  final String? sourceStop;
  final String? destStop;
  final Direction? direction;

  bool get canSubmit =>
      selectedConveyance != null &&
      sourceStop != null &&
      destStop != null &&
      sourceStop != destStop &&
      direction != null;

  const RouteSelectionState({
    this.status = RouteSelectionStatus.loading,
    this.routeTypes = const [],
    this.conveyances = const [],
    this.stops = const [],
    this.selectedType,
    this.selectedConveyance,
    this.sourceStop,
    this.destStop,
    this.direction,
  });

  RouteSelectionState copyWith({
    RouteSelectionStatus? status,
    List<RouteType>? routeTypes,
    List<Conveyance>? conveyances,
    List<String>? stops,
    RouteType? selectedType,
    Conveyance? selectedConveyance,
    String? sourceStop,
    String? destStop,
    Direction? direction,
  }) =>
      RouteSelectionState(
        status: status ?? this.status,
        routeTypes: routeTypes ?? this.routeTypes,
        conveyances: conveyances ?? this.conveyances,
        stops: stops ?? this.stops,
        selectedType: selectedType ?? this.selectedType,
        selectedConveyance: selectedConveyance ?? this.selectedConveyance,
        sourceStop: sourceStop ?? this.sourceStop,
        destStop: destStop ?? this.destStop,
        direction: direction ?? this.direction,
      );
}
