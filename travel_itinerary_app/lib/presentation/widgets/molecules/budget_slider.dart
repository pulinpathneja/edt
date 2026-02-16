import 'package:flutter/material.dart';

import '../../../theme/colors/app_colors.dart';
import '../../../theme/spacing/app_spacing.dart';

/// Budget level slider
class BudgetSlider extends StatelessWidget {
  final int value;
  final ValueChanged<int>? onChanged;
  final int min;
  final int max;

  const BudgetSlider({
    super.key,
    required this.value,
    this.onChanged,
    this.min = 1,
    this.max = 5,
  });

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // Budget level display
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text(
              _getBudgetLabel(),
              style: TextStyle(
                fontSize: 16,
                fontWeight: FontWeight.w600,
                color: AppColors.textPrimary,
              ),
            ),
            Container(
              padding: const EdgeInsets.symmetric(
                horizontal: AppSpacing.sm,
                vertical: AppSpacing.xs,
              ),
              decoration: BoxDecoration(
                color: _getBudgetColor().withOpacity(0.15),
                borderRadius: BorderRadius.circular(AppSpacing.radiusSM),
              ),
              child: Text(
                '\$' * value,
                style: TextStyle(
                  fontSize: 14,
                  fontWeight: FontWeight.w600,
                  color: _getBudgetColor(),
                ),
              ),
            ),
          ],
        ),
        const SizedBox(height: AppSpacing.md),

        // Slider
        SliderTheme(
          data: SliderTheme.of(context).copyWith(
            activeTrackColor: _getBudgetColor(),
            inactiveTrackColor: AppColors.border,
            thumbColor: _getBudgetColor(),
            overlayColor: _getBudgetColor().withOpacity(0.1),
            trackHeight: 6,
            thumbShape: const RoundSliderThumbShape(enabledThumbRadius: 12),
            overlayShape: const RoundSliderOverlayShape(overlayRadius: 24),
          ),
          child: Slider(
            value: value.toDouble(),
            min: min.toDouble(),
            max: max.toDouble(),
            divisions: max - min,
            onChanged: onChanged != null
                ? (v) => onChanged!(v.round())
                : null,
          ),
        ),

        // Labels
        Padding(
          padding: const EdgeInsets.symmetric(horizontal: 8),
          child: Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                'Budget',
                style: TextStyle(
                  fontSize: 12,
                  color: AppColors.textTertiary,
                ),
              ),
              Text(
                'Luxury',
                style: TextStyle(
                  fontSize: 12,
                  color: AppColors.textTertiary,
                ),
              ),
            ],
          ),
        ),
      ],
    );
  }

  String _getBudgetLabel() {
    return switch (value) {
      1 => 'Budget-Friendly',
      2 => 'Economical',
      3 => 'Moderate',
      4 => 'Upscale',
      5 => 'Luxury',
      _ => 'Moderate',
    };
  }

  Color _getBudgetColor() {
    return switch (value) {
      1 => AppColors.success,
      2 => const Color(0xFF7A9E5D),
      3 => AppColors.primary,
      4 => AppColors.gold,
      5 => const Color(0xFFC8A951),
      _ => AppColors.primary,
    };
  }
}
