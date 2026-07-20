enum AlertSeverity {
    severe,
    warning,
    info,
    unknown;

    static AlertSeverity fromCode(String? code) => switch (code) {
        'SEVERE'  => AlertSeverity.severe,
        'WARNING' => AlertSeverity.warning,
        'INFO'    => AlertSeverity.info,
        _         => AlertSeverity.unknown,
    };
}


class Alert {
    final String id;
    final String cause;
    final String effect;
    final AlertSeverity severity;
    final String headerText;
    final String descriptionText;
    final String? url;

    Alert({
        required this.id,
        required this.cause,
        required this.effect,
        required this.severity,
        required this.headerText,
        required this.descriptionText,
        this.url,
    });
}
