import 'dart:io';

const _noExecutableLines = <String>{
  'lib/config/datappy_config.dart',
  'lib/domain/repositories/i_alert.dart',
  'lib/domain/repositories/i_city.dart',
  'lib/domain/repositories/i_conveyance.dart',
  'lib/domain/repositories/i_direction.dart',
  'lib/domain/repositories/i_favorites_store.dart',
  'lib/domain/repositories/i_selection_store.dart',
  'lib/domain/repositories/i_stop_name.dart',
  'lib/domain/repositories/i_stop_update.dart',
  'lib/domain/repositories/i_theme_store.dart',
};

class _Cov {
  int hit = 0;
  int total = 0;
  final List<int> missing = [];
}

void main() {
  final lcov = File('coverage/lcov.info');
  if (!lcov.existsSync()) {
    stderr.writeln('coverage/lcov.info not found — run `flutter test --coverage` first.');
    exit(1);
  }

  final reported = <String, _Cov>{};
  String? current;
  for (final line in lcov.readAsLinesSync()) {
    if (line.startsWith('SF:')) {
      var path = line.substring(3).trim();
      final idx = path.indexOf('lib/');
      if (idx >= 0) path = path.substring(idx);
      current = path;
      reported.putIfAbsent(current, () => _Cov());
    } else if (line.startsWith('DA:') && current != null) {
      final parts = line.substring(3).split(',');
      final lineNo = int.parse(parts[0]);
      final count = int.parse(parts[1]);
      final cov = reported[current]!;
      cov.total++;
      if (count > 0) {
        cov.hit++;
      } else {
        cov.missing.add(lineNo);
      }
    }
  }

  final libFiles = Directory('lib')
      .listSync(recursive: true)
      .whereType<File>()
      .map((f) => f.path.replaceAll(r'\', '/'))
      .where((p) => p.endsWith('.dart'))
      .toList()
    ..sort();

  var totalHit = 0;
  var totalTotal = 0;
  final problems = <String>[];

  for (final path in libFiles) {
    final cov = reported[path];
    if (cov == null) {
      if (_noExecutableLines.contains(path)) continue;
      problems.add('MISSING FROM REPORT   $path');
      continue;
    }
    totalHit += cov.hit;
    totalTotal += cov.total;
    if (cov.hit < cov.total) {
      final pct = (100 * cov.hit / cov.total).toStringAsFixed(1);
      final miss = cov.missing.take(15).join(', ');
      problems.add('$pct%   $path   missing lines: $miss');
    }
  }

  final totalPct = totalTotal == 0 ? 100.0 : 100 * totalHit / totalTotal;

  if (problems.isEmpty && totalPct >= 100) {
    stdout.writeln('Coverage OK: 100.00% of lib/ '
        '($totalHit/$totalTotal lines across ${libFiles.length} files).');
    exit(0);
  }

  stdout.writeln('Coverage below 100%:\n');
  for (final p in problems) {
    stdout.writeln('  $p');
  }
  stdout.writeln('\nTOTAL: ${totalPct.toStringAsFixed(2)}% ($totalHit/$totalTotal lines).');
  exit(1);
}
