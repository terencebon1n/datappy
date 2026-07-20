import 'package:frontend/domain/alert.dart' show Alert, AlertSeverity;


class AlertResponse {
    final String id;
    final String cause;
    final String effect;
    final String severity;
    final String headerText;
    final String descriptionText;
    final String? url;

    AlertResponse({
        required this.id,
        required this.cause,
        required this.effect,
        required this.severity,
        required this.headerText,
        required this.descriptionText,
        this.url,
    });

    factory AlertResponse.fromJson(Map<String, dynamic> json) => AlertResponse(
        id: json['id'],
        cause: json['cause'] ?? 'UNKNOWN_CAUSE',
        effect: json['effect'] ?? 'UNKNOWN_EFFECT',
        severity: json['severity'] ?? 'UNKNOWN_SEVERITY',
        headerText: json['header_text'] ?? '',
        descriptionText: json['description_text'] ?? '',
        url: json['url'],
    );

    Alert toDomain() => Alert(
        id: id,
        cause: cause,
        effect: effect,
        severity: AlertSeverity.fromCode(severity),
        headerText: headerText,
        descriptionText: descriptionText,
        url: url,
    );
}
