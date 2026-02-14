import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';

import '../../../theme/colors/app_colors.dart';
import '../../../theme/spacing/app_spacing.dart';
import '../atoms/app_chip.dart';

/// Chip item data
class ChipItem {
  final String id;
  final String label;
  final String? icon;
  final Color? color;

  const ChipItem({
    required this.id,
    required this.label,
    this.icon,
    this.color,
  });
}

/// Multi-select chip group for vibes, etc.
class MultiSelectChipGroup extends StatelessWidget {
  final List<ChipItem> items;
  final Set<String> selectedIds;
  final ValueChanged<Set<String>>? onSelectionChanged;
  final int? maxSelections;
  final bool showCheckmark;
  final String? helperText;

  const MultiSelectChipGroup({
    super.key,
    required this.items,
    required this.selectedIds,
    this.onSelectionChanged,
    this.maxSelections,
    this.showCheckmark = true,
    this.helperText,
  });

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        if (helperText != null) ...[
          Text(
            helperText!,
            style: TextStyle(
              fontSize: 12,
              color: AppColors.textTertiary,
            ),
          ),
          const SizedBox(height: AppSpacing.sm),
        ],
        Wrap(
          spacing: AppSpacing.sm,
          runSpacing: AppSpacing.sm,
          children: items.asMap().entries.map((entry) {
            final index = entry.key;
            final item = entry.value;
            final isSelected = selectedIds.contains(item.id);
            final canSelect = maxSelections == null ||
                selectedIds.length < maxSelections! ||
                isSelected;

            return AppChip(
              label: item.label,
              icon: item.icon,
              isSelected: isSelected,
              selectedColor: item.color ?? AppColors.vibeColor(item.id),
              showCheckmark: showCheckmark,
              onTap: canSelect
                  ? () => _onChipTap(item.id, isSelected)
                  : null,
            ).animate(delay: Duration(milliseconds: index * 50)).fadeIn().scale(
                  begin: const Offset(0.9, 0.9),
                  duration: const Duration(milliseconds: 200),
                );
          }).toList(),
        ),
        if (maxSelections != null) ...[
          const SizedBox(height: AppSpacing.sm),
          Text(
            '${selectedIds.length}/$maxSelections selected',
            style: TextStyle(
              fontSize: 12,
              color: selectedIds.length >= maxSelections!
                  ? AppColors.warning
                  : AppColors.textTertiary,
            ),
          ),
        ],
      ],
    );
  }

  void _onChipTap(String id, bool isCurrentlySelected) {
    if (onSelectionChanged == null) return;

    final newSelection = Set<String>.from(selectedIds);
    if (isCurrentlySelected) {
      newSelection.remove(id);
    } else {
      newSelection.add(id);
    }
    onSelectionChanged!(newSelection);
  }
}
