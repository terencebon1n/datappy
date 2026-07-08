#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

out=test/coverage_helper_test.dart
{
  echo "// ignore_for_file: unused_import"
  echo
  find lib -name '*.dart' | sort | sed "s#^lib/#import 'package:frontend/#; s#\$#';#"
  echo
  echo "void main() {}"
} > "$out"

echo "Wrote $out ($(grep -c "^import" "$out") imports)."
