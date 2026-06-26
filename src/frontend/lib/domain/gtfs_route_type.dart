/// GTFS `route_type` taxonomy (standard values 0-7), mirroring the backend
/// `RouteTypeId`. Extended GTFS route types (e.g. 11, 12, 100+) resolve to
/// `null` via [fromId] and are treated as a generic conveyance by the UI.
enum GtfsRouteType {
  tram(0),
  subway(1),
  rail(2),
  bus(3),
  ferry(4),
  cableCar(5),
  gondola(6),
  funicular(7);

  const GtfsRouteType(this.id);

  final int id;

  static GtfsRouteType? fromId(int id) {
    for (final type in values) {
      if (type.id == id) return type;
    }
    return null;
  }
}
