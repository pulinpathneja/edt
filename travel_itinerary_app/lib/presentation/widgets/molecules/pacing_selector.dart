import 'package:flutter/material.dart';

import '../../../theme/colors/app_colors.dart';
import '../../../theme/spacing/app_spacing.dart';

/// Pacing option data
class PacingOption {
  final String id;
  final String label;
  final String description;
  final IconData icon;

  const PacingOption({
    required this.id,
    required this.label,
    required this.description,
    required this.icon,
  });
}

/// Default pacing options
const defaultPacingOptions = [
  PacingOption(
    id: 'slow',
    label: 'Relaxed',
    description: 'Fewer activities, more leisure time',
    icon: Icons.spa_outlined,
  ),
  PacingOption(
    id: 'moderate',
    label: 'Balanced',
    description: 'Mix of activities and downtime',
    icon: Icons.balance_outlined,
  ),
  PacingOption(
    id: 'fast',
    label: 'Action-packed',
    description: 'Maximize activities each day',
    icon: Icons.flash_on_outlined,
  ),
];

/// Pacing selector widget
class PacingSelector extends StatelessWidget {
  final String? selectedId;
  final ValueChanged<String>? onChanged;
  final List<PacingOption> options;

  const PacingSelector({
    super.key,
    this.selectedId,
    this.onChanged,
    this.options = defaultPacingOptions,
  });

  @override
  Widget build(BuildContext context) {
    return Row(
      children: options.asMap().entries.map((entry) {
        final index = entry.key;
        final option = entry.value;
        final isSelected = selectedId == option.id;
        final isFirst = index == 0;
        final isLast = index == options.length - 1;

        return Expanded(
          child: GestureDetector(
            onTap: () => onChanged?.call(option.id),
            child: AnimatedContainer(
              duration: const Duration(milliseconds: 200),
              curve: Curves.easeOutCubic,
              padding: const EdgeInsets.all(AppSpacing.md),
              decoration: BoxDecoration(
                color: isSelected
                    ? AppColors.primary.withOpacity(0.1)
                    : AppColors.surface,
                borderRadius: BorderRadius.horizontal(
                  left: isFirst
                      ? const Radius.circular(AppSpacing.radiusMD)
                      : Radius.zero,
                  right: isLast
                      ? const Radius.circular(AppSpacing.radiusMD)
                      : Radius.zero,
                ),
                border: Border.all(
                  color: isSelected ? AppColors.primary : AppColors.border,
                  width: isSelected ? 2 : 1,
                ),
              ),
              child: Column(
                children: [
                  Icon(
                    option.icon,
                    size: 24,
                    color: isSelected ? AppColors.primary : AppColors.textSecondary,
                  ),
                  const SizedBox(height: AppSpacing.sm),
                  Text(
                    option.label,
                    style: TextStyle(
                      fontSize: 14,
                      fontWeight: isSelected ? FontWeight.w600 : FontWeight.w500,
                      color: isSelected ? AppColors.primary : AppColors.textPrimary,
                    ),
                    textAlign: TextAlign.center,
                  ),
                  const SizedBox(height: AppSpacing.xs),
                  Text(
                    option.description,
                    style: TextStyle(
                      fontSize: 11,
                      color: AppColors.textTertiary,
                    ),
                    textAlign: TextAlign.center,
                    maxLines: 2,
                    overflow: TextOverflow.ellipsis,
                  ),
                ],
              ),
            ),
          ),
        );
      }).toList(),
    );
  }
}
