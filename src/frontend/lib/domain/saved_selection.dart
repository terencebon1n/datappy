import 'package:frontend/domain/city.dart' show City;
import 'package:frontend/domain/conveyance.dart' show Conveyance;
import 'package:frontend/domain/direction.dart' show Direction;


class SavedSelection {
    final City city;
    final Conveyance conveyance;
    final String sourceStop;
    final String destStop;
    final Direction direction;

    SavedSelection({
        required this.city,
        required this.conveyance,
        required this.sourceStop,
        required this.destStop,
        required this.direction,
    });

    Map<String, dynamic> toJson() => {
        'city': {'name': city.name},
        'conveyance': {
            'id': conveyance.id,
            'shortName': conveyance.shortName,
            'longName': conveyance.longName,
            'colorValue': conveyance.colorValue,
            'typeId': conveyance.typeId,
            'typeName': conveyance.typeName,
        },
        'sourceStop': sourceStop,
        'destStop': destStop,
        'direction': {
            'directionId': direction.directionId,
            'stopIdOrigin': direction.stopIdOrigin,
            'stopIdDestination': direction.stopIdDestination,
        },
    };

    factory SavedSelection.fromJson(Map<String, dynamic> json) {
        final conveyance = json['conveyance'] as Map<String, dynamic>;
        final direction = json['direction'] as Map<String, dynamic>;
        return SavedSelection(
            city: City(name: (json['city'] as Map<String, dynamic>)['name'] as String),
            conveyance: Conveyance(
                id: conveyance['id'] as String,
                shortName: conveyance['shortName'] as String,
                longName: conveyance['longName'] as String,
                colorValue: conveyance['colorValue'] as int,
                typeId: conveyance['typeId'] as int,
                typeName: conveyance['typeName'] as String,
            ),
            sourceStop: json['sourceStop'] as String,
            destStop: json['destStop'] as String,
            direction: Direction(
                directionId: direction['directionId'] as int,
                stopIdOrigin: direction['stopIdOrigin'] as String,
                stopIdDestination: direction['stopIdDestination'] as String,
            ),
        );
    }

    @override
    bool operator ==(Object other) =>
        other is SavedSelection &&
        other.city.name == city.name &&
        other.conveyance.id == conveyance.id &&
        other.sourceStop == sourceStop &&
        other.destStop == destStop &&
        other.direction.directionId == direction.directionId;

    @override
    int get hashCode => Object.hash(
        city.name,
        conveyance.id,
        sourceStop,
        destStop,
        direction.directionId,
    );
}
