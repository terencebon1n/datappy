import 'package:flutter_test/flutter_test.dart';

import 'package:frontend/domain/gtfs_route_type.dart';

void main() {
  test('fromId maps every known GTFS route type id', () {
    expect(GtfsRouteType.fromId(0), GtfsRouteType.tram);
    expect(GtfsRouteType.fromId(1), GtfsRouteType.subway);
    expect(GtfsRouteType.fromId(2), GtfsRouteType.rail);
    expect(GtfsRouteType.fromId(3), GtfsRouteType.bus);
    expect(GtfsRouteType.fromId(4), GtfsRouteType.ferry);
    expect(GtfsRouteType.fromId(5), GtfsRouteType.cableCar);
    expect(GtfsRouteType.fromId(6), GtfsRouteType.gondola);
    expect(GtfsRouteType.fromId(7), GtfsRouteType.funicular);
  });

  test('fromId returns null for an unknown id', () {
    expect(GtfsRouteType.fromId(99), isNull);
    expect(GtfsRouteType.fromId(-1), isNull);
  });
}
