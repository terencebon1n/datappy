import 'package:flutter/material.dart';

import 'package:frontend/domain/conveyance.dart' show Conveyance;


class ConveyanceResponse {
    final String id;
    final String shortName;
    final String longName;
    final Color color;

    ConveyanceResponse({
        required this.id,
        required this.shortName,
        required this.longName,
        required this.color,
    });

    factory ConveyanceResponse.fromJson(Map<String, dynamic> json) {
        final colorStr = json['color'] as String?;
          
        final colorInt = colorStr != null 
            ? int.tryParse('0xFF${colorStr.replaceFirst('#', '')}') 
            : null;

        return ConveyanceResponse(
            id: json['id'],
            shortName: json['short_name'],
            longName: json['long_name'],
            color: colorInt != null ? Color(colorInt) : const Color(0xFFFFFFFF),
        );
    }

    Conveyance toDomain() => Conveyance(
        id: id,
        shortName: shortName,
        longName: longName,
        color: color,
    );
}
