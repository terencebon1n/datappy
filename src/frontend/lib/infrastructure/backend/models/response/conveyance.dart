import 'package:frontend/domain/conveyance.dart' show Conveyance;


class ConveyanceResponse {
    final String id;
    final String shortName;
    final String longName;

    ConveyanceResponse({
        required this.id,
        required this.shortName,
        required this.longName,
    });

    factory ConveyanceResponse.fromJson(Map<String, dynamic> json) => ConveyanceResponse(
        id: json['id'],
        shortName: json['short_name'],
        longName: json['long_name'],
    );

    Conveyance toDomain() => Conveyance(
        id: id,
        shortName: shortName,
        longName: longName,
    );
}
