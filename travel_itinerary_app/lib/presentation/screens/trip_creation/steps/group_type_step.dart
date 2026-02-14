import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';

import '../../../../domain/entities/persona_config.dart';
import '../../../../theme/colors/app_colors.dart';
import '../../../../theme/spacing/app_spacing.dart';
import '../../../widgets/organisms/group_type_grid.dart';

/// Step 2: Group type and size
class GroupTypeStep extends StatelessWidget {
  final List<GroupTypeOption> options;
  final String selectedType;
  final int groupSize;
  final bool hasKids;
  final bool hasSeniors;
  final ValueChanged<String> onTypeChanged;
  final ValueChanged<int> onGroupSizeChanged;
  final ValueChanged<bool> onHasKidsChanged;
  final ValueChanged<bool> onHasSeniorsChanged;
  final int maxGroupSize;

  const GroupTypeStep({
    super.key,
    required this.options,
    required this.selectedType,
    required this.groupSize,
    required this.hasKids,
    required this.hasSeniors,
    required this.onTypeChanged,
    required this.onGroupSizeChanged,
    required this.onHasKidsChanged,
    required this.onHasSeniorsChanged,
    this.maxGroupSize = 20,
  });

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // Group type grid
        GroupTypeGrid(
          options: options,
          selectedId: selectedType,
          onSelected: onTypeChanged,
        ),

        const SizedBox(height: AppSpacing.xl),

        // Group size slider
        Text(
          'Group Size',
          style: TextStyle(
            fontSize: 14,
            fontWeight: FontWeight.w600,
            color: AppColors.textSecondary,
          ),
        )
            .animate(delay: const Duration(milliseconds: 300))
            .fadeIn()
            .slideX(begin: -0.1),
        const SizedBox(height: AppSpacing.md),

        _GroupSizeSelector(
          value: groupSize,
          maxValue: maxGroupSize,
          onChanged: onGroupSizeChanged,
        )
            .animate(delay: const Duration(milliseconds: 350))
            .fadeIn()
            .slideX(begin: -0.1),

        const SizedBox(height: AppSpacing.xl),

        // Additional options
        Text(
          'Group Composition',
          style: TextStyle(
            fontSize: 14,
            fontWeight: FontWeight.w600,
            color: AppColors.textSecondary,
          ),
        )
            .animate(delay: const Duration(milliseconds: 400))
            .fadeIn()
            .slideX(begin: -0.1),
        const SizedBox(height: AppSpacing.sm),

        _ToggleOption(
          label: 'Traveling with children',
          sublabel: 'We\'ll include kid-friendly activities',
          icon: Icons.child_care,
          value: hasKids,
          onChanged: onHasKidsChanged,
        )
            .animate(delay: const Duration(milliseconds: 450))
            .fadeIn()
            .slideX(begin: -0.1),

        const SizedBox(height: AppSpacing.sm),

        _ToggleOption(
          label: 'Traveling with seniors',
          sublabel: 'We\'ll consider accessibility needs',
          icon: Icons.elderly,
          value: hasSeniors,
          onChanged: onHasSeniorsChanged,
        )
            .animate(delay: const Duration(milliseconds: 500))
            .fadeIn()
            .slideX(begin: -0.1),
      ],
    );
  }
}

class _GroupSizeSelector extends StatelessWidget {
  final int value;
  final int maxValue;
  final ValueChanged<int> onChanged;

  const _GroupSizeSelector({
    required this.value,
    required this.maxValue,
    required this.onChanged,
  });

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        // Decrement button
        _SizeButton(
          icon: Icons.remove,
          onPressed: value > 1 ? () => onChanged(value - 1) : null,
        ),

        // Value display
        Expanded(
          child: Container(
            margin: const EdgeInsets.symmetric(horizontal: AppSpacing.md),
            padding: const EdgeInsets.symmetric(vertical: AppSpacing.md),
            decoration: BoxDecoration(
              color: AppColors.surfaceVariant,
              borderRadius: BorderRadius.circular(AppSpacing.radiusMD),
            ),
            child: Column(
              children: [
                Text(
                  '$value',
                  style: const TextStyle(
                    fontSize: 32,
                    fontWeight: FontWeight.w700,
                    color: AppColors.primary,
                  ),
                ),
                Text(
                  value == 1 ? 'person' : 'people',
                  style: TextStyle(
                    fontSize: 14,
                    color: AppColors.textSecondary,
                  ),
                ),
              ],
            ),
          ),
        ),

        // Increment button
        _SizeButton(
          icon: Icons.add,
          onPressed: value < maxValue ? () => onChanged(value + 1) : null,
        ),
      ],
    );
  }
}

class _SizeButton extends StatelessWidget {
  final IconData icon;
  final VoidCallback? onPressed;

  const _SizeButton({
    required this.icon,
    this.onPressed,
  });

  @override
  Widget build(BuildContext context) {
    final isEnabled = onPressed != null;

    return GestureDetector(
      onTap: onPressed,
      child: Container(
        width: 48,
        height: 48,
        decoration: BoxDecoration(
          color: isEnabled ? AppColors.primary : AppColors.surfaceVariant,
          shape: BoxShape.circle,
        ),
        child: Icon(
          icon,
          color: isEnabled ? AppColors.white : AppColors.textDisabled,
        ),
      ),
    );
  }
}

class _ToggleOption extends StatelessWidget {
  final String label;
  final String sublabel;
  final IconData icon;
  final bool value;
  final ValueChanged<bool> onChanged;

  const _ToggleOption({
    required this.label,
    required this.sublabel,
    required this.icon,
    required this.value,
    required this.onChanged,
  });

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: () => onChanged(!value),
      child: Container(
        padding: const EdgeInsets.all(AppSpacing.md),
        decoration: BoxDecoration(
          color: value
              ? AppColors.primary.withOpacity(0.1)
              : AppColors.surface,
          borderRadius: BorderRadius.circular(AppSpacing.radiusMD),
          border: Border.all(
            color: value ? AppColors.primary : AppColors.border,
          ),
        ),
        child: Row(
          children: [
            Icon(
              icon,
              color: value ? AppColors.primary : AppColors.textSecondary,
            ),
            const SizedBox(width: AppSpacing.md),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    label,
                    style: TextStyle(
                      fontSize: 14,
                      fontWeight: FontWeight.w600,
                      color: value ? AppColors.primary : AppColors.textPrimary,
                    ),
                  ),
                  Text(
                    sublabel,
                    style: TextStyle(
                      fontSize: 12,
                      color: AppColors.textTertiary,
                    ),
                  ),
                ],
              ),
            ),
            Switch(
              value: value,
              onChanged: onChanged,
              activeColor: AppColors.primary,
            ),
          ],
        ),
      ),
    );
  }
}
