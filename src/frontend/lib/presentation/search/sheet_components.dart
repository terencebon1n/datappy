import 'package:flutter/material.dart';
import 'package:frontend/presentation/theme/colors.dart';

class SheetLabel extends StatelessWidget {
  const SheetLabel(this.text, {super.key});
  final String text;

  @override
  Widget build(BuildContext context) {
    return Text(
      text.toUpperCase(),
      style: const TextStyle(
        fontSize: 9,
        color: TransitColors.textMuted,
        letterSpacing: 0.8,
      ),
    );
  }
}

class SheetDropdown<T> extends StatelessWidget {
  const SheetDropdown({
    super.key,
    required this.hint,
    required this.value,
    required this.items,
    required this.label,
    required this.onChanged,
  });

  final String              hint;
  final T?                  value;
  final List<T>             items;
  final String Function(T)  label;
  final ValueChanged<T>?    onChanged;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 2),
      decoration: BoxDecoration(
        color: TransitColors.surfaceHigh,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: TransitColors.border),
      ),
      child: DropdownButtonHideUnderline(
        child: DropdownButton<T>(
          value: value,
          hint: Text(hint, style: const TextStyle(fontSize: 13, color: TransitColors.textMuted)),
          items: items
              .map((item) => DropdownMenuItem<T>(
                    value: item,
                    child: Text(
                      label(item),
                      style: const TextStyle(fontSize: 13, color: TransitColors.textPrimary),
                      overflow: TextOverflow.ellipsis,
                    ),
                  ))
              .toList(),
          onChanged: onChanged == null ? null : (T? val) {
            if (val != null) onChanged!(val);
          },
          dropdownColor: TransitColors.surfaceHigh,
          iconEnabledColor: TransitColors.textSecondary,
          iconDisabledColor: TransitColors.textMuted,
          isExpanded: true,
          style: const TextStyle(fontSize: 13, color: TransitColors.textPrimary),
        ),
      ),
    );
  }
}
