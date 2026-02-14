import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';

import '../../../../domain/entities/persona_config.dart' as domain;
import '../../../../theme/colors/app_colors.dart';
import '../../../../theme/spacing/app_spacing.dart';
import '../../../widgets/molecules/budget_slider.dart';
import '../../../widgets/molecules/pacing_selector.dart';

/// Step 4: Pacing and budget preferences
class PreferencesStep extends StatelessWidget {
  final List<domain.PacingOption> pacingOptions;
  final String selectedPacing;
  final int budgetLevel;
  final int budgetMin;
  final int budgetMax;
  final ValueChanged<String> onPacingChanged;
  final ValueChanged<int> onBudgetChanged;

  const PreferencesStep({
    super.key,
    required this.pacingOptions,
    required this.selectedPacing,
    required this.budgetLevel,
    required this.budgetMin,
    required this.budgetMax,
    required this.onPacingChanged,
    required this.onBudgetChanged,
  });

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // Pacing selection
        Text(
          'Travel Pace',
          style: TextStyle(
            fontSize: 14,
            fontWeight: FontWeight.w600,
            color: AppColors.textSecondary,
          ),
        )
            .animate()
            .fadeIn()
            .slideX(begin: -0.1),
        const SizedBox(height: AppSpacing.sm),

        Text(
          'How many activities per day?',
          style: TextStyle(
            fontSize: 12,
            color: AppColors.textTertiary,
          ),
        )
            .animate(delay: const Duration(milliseconds: 50))
            .fadeIn()
            .slideX(begin: -0.1),
        const SizedBox(height: AppSpacing.md),

        PacingSelector(
          selectedId: selectedPacing,
          onChanged: onPacingChanged,
          options: _mapPacingOptions(pacingOptions),
        )
            .animate(delay: const Duration(milliseconds: 100))
            .fadeIn()
            .slideX(begin: -0.1),

        const SizedBox(height: AppSpacing.xxl),

        // Budget slider
        Text(
          'Budget Level',
          style: TextStyle(
            fontSize: 14,
            fontWeight: FontWeight.w600,
            color: AppColors.textSecondary,
          ),
        )
            .animate(delay: const Duration(milliseconds: 200))
            .fadeIn()
            .slideX(begin: -0.1),
        const SizedBox(height: AppSpacing.sm),

        Text(
          'This helps us recommend appropriate venues',
          style: TextStyle(
            fontSize: 12,
            color: AppColors.textTertiary,
          ),
        )
            .animate(delay: const Duration(milliseconds: 250))
            .fadeIn()
            .slideX(begin: -0.1),
        const SizedBox(height: AppSpacing.lg),

        BudgetSlider(
          value: budgetLevel,
          min: budgetMin,
          max: budgetMax,
          onChanged: onBudgetChanged,
        )
            .animate(delay: const Duration(milliseconds: 300))
            .fadeIn()
            .slideX(begin: -0.1),

        const SizedBox(height: AppSpacing.xl),

        // Info card
        Container(
          padding: const EdgeInsets.all(AppSpacing.md),
          decoration: BoxDecoration(
            color: AppColors.info.withOpacity(0.1),
            borderRadius: BorderRadius.circular(AppSpacing.radiusMD),
            border: Border.all(color: AppColors.info.withOpacity(0.3)),
          ),
          child: Row(
            children: [
              Icon(
                Icons.info_outline,
                color: AppColors.info,
                size: 20,
              ),
              const SizedBox(width: AppSpacing.sm),
              Expanded(
                child: Text(
                  'These preferences help us create a personalized itinerary that matches your travel style.',
                  style: TextStyle(
                    fontSize: 12,
                    color: AppColors.info,
                  ),
                ),
              ),
            ],
          ),
        )
            .animate(delay: const Duration(milliseconds: 400))
            .fadeIn()
            .slideY(begin: 0.1),
      ],
    );
  }

  List<PacingOption> _mapPacingOptions(List<domain.PacingOption> options) {
    if (options.isEmpty) return defaultPacingOptions;

    return options.map((o) {
      final icon = switch (o.id) {
        'slow' => Icons.spa_outlined,
        'moderate' => Icons.balance_outlined,
        'fast' => Icons.flash_on_outlined,
        _ => Icons.schedule,
      };

      return PacingOption(
        id: o.id,
        label: o.label,
        description: o.description ?? '',
        icon: icon,
      );
    }).toList();
  }
}
