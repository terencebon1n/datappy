import 'package:frontend/domain/conveyance.dart' show Conveyance;


class ConveyanceResponse {
    final String id;
    final String shortName;
    final String longName;
    final int colorValue;
    final int typeId;
    final String typeName;

    ConveyanceResponse({
        required this.id,
        required this.shortName,
        required this.longName,
        required this.colorValue,
        required this.typeId,
        required this.typeName,
    });

    factory ConveyanceResponse.fromJson(Map<String, dynamic> json) {
        final colorStr = json['color'] as String?;

        final colorValue = colorStr != null
            ? (int.tryParse('0xFF${colorStr.replaceFirst('#', '')}') ?? 0xFFFFFFFF)
            : 0xFFFFFFFF;

        return ConveyanceResponse(
            id: json['id'],
            shortName: json['short_name'],
            longName: json['long_name'],
            colorValue: colorValue,
            typeId: json['type'] as int,
            typeName: json['type_name'] as String,
        );
    }

    Conveyance toDomain() => Conveyance(
        id: id,
        shortName: shortName,
        longName: longName,
        colorValue: colorValue,
        typeId: typeId,
        typeName: typeName,
    );
}
