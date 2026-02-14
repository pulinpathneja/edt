import 'package:flutter/material.dart';

import '../../../domain/entities/persona_config.dart';
import '../../../theme/colors/app_colors.dart';
import '../molecules/multi_select_chip_group.dart';

/// Vibe selection grid with multi-select chips
class VibeSelectionGrid extends StatelessWidget {
  final List<VibeOption> options;
  final Set<String> selectedIds;
  final ValueChanged<Set<String>>? onSelectionChanged;
  final int maxSelections;

  const VibeSelectionGrid({
    super.key,
    required this.options,
    required this.selectedIds,
    this.onSelectionChanged,
    this.maxSelections = 5,
  });

  @override
  Widget build(BuildContext context) {
    final chipItems = options.map((option) {
      return ChipItem(
        id: option.id,
        label: option.label,
        icon: option.icon,
        color: AppColors.vibeColor(option.id),
      );
    }).toList();

    return MultiSelectChipGroup(
      items: chipItems,
      selectedIds: selectedIds,
      onSelectionChanged: onSelectionChanged,
      maxSelections: maxSelections,
      showCheckmark: true,
      helperText: 'Select up to $maxSelections vibes that match your travel style',
    );
  }
}
