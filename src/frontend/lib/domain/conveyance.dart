class Conveyance {
    final String id;
    final String shortName;
    final String longName;
    final int colorValue; // ARGB value; wrapped in a Color by the UI layer
    final int typeId;
    final String typeName;

    Conveyance({
        required this.id,
        required this.shortName,
        required this.longName,
        required this.colorValue,
        required this.typeId,
        required this.typeName,
    });
}
