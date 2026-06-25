import 'package:flutter/material.dart';

class Conveyance {
    final String id;
    final String shortName;
    final String longName;
    final Color color;
    final int typeId;
    final String typeName;

    Conveyance({
        required this.id,
        required this.shortName,
        required this.longName,
        required this.color,
        required this.typeId,
        required this.typeName,
    });
}
