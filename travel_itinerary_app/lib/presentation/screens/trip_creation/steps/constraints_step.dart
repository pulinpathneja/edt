import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';

import '../../../../theme/colors/app_colors.dart';
import '../../../../theme/spacing/app_spacing.dart';

/// Step 5: Special constraints and preferences
class ConstraintsStep extends StatelessWidget {
  final bool avoidHeat;
  final bool mobilityConstraints;
  final bool avoidCrowds;
  final bool preferOutdoor;
  final bool preferIndoor;
  final ValueChanged<bool> onAvoidHeatChanged;
  final ValueChanged<bool> onMobilityConstraintsChanged;
  final ValueChanged<bool> onAvoidCrowdsChanged;
  final ValueChanged<bool> onPreferOutdoorChanged;
  final ValueChanged<bool> onPreferIndoorChanged;

  const ConstraintsStep({
    super.key,
    required this.avoidHeat,
    required this.mobilityConstraints,
    required this.avoidCrowds,
    required this.preferOutdoor,
    required this.preferIndoor,
    required this.onAvoidHeatChanged,
    required this.onMobilityConstraintsChanged,
    required this.onAvoidCrowdsChanged,
    required this.onPreferOutdoorChanged,
    required this.onPreferIndoorChanged,
  });

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // Comfort preferences
        Text(
          'Comfort Preferences',
          style: TextStyle(
            fontSize: 14,
            fontWeight: FontWeight.w600,
            color: AppColors.textSecondary,
          ),
        )
            .animate()
            .fadeIn()
            .slideX(begin: -0.1),
        const SizedBox(height: AppSpacing.md),

        _ConstraintCard(
          icon: Icons.thermostat_outlined,
          title: 'Avoid peak heat hours',
          description: 'Schedule outdoor activities during cooler times',
          value: avoidHeat,
          onChanged: onAvoidHeatChanged,
          delay: const Duration(milliseconds: 100),
        ),

        const SizedBox(height: AppSpacing.sm),

        _ConstraintCard(
          icon: Icons.accessible,
          title: 'Mobility considerations',
          description: 'Prefer accessible venues and shorter walking distances',
          value: mobilityConstraints,
          onChanged: onMobilityConstraintsChanged,
          delay: const Duration(milliseconds: 150),
        ),

        const SizedBox(height: AppSpacing.sm),

        _ConstraintCard(
          icon: Icons.groups_outlined,
          title: 'Avoid crowded places',
          description: 'Prefer less touristy spots and off-peak times',
          value: avoidCrowds,
          onChanged: onAvoidCrowdsChanged,
          delay: const Duration(milliseconds: 200),
        ),

        const SizedBox(height: AppSpacing.xl),

        // Activity preference
        Text(
          'Activity Preference',
          style: TextStyle(
            fontSize: 14,
            fontWeight: FontWeight.w600,
            color: AppColors.textSecondary,
          ),
        )
            .animate(delay: const Duration(milliseconds: 250))
            .fadeIn()
            .slideX(begin: -0.1),
        const SizedBox(height: AppSpacing.md),

        _ConstraintCard(
          icon: Icons.park_outlined,
          title: 'Prefer outdoor activities',
          description: 'More parks, walking tours, and open-air venues',
          value: preferOutdoor,
          onChanged: (value) {
            onPreferOutdoorChanged(value);
            if (value && preferIndoor) {
              onPreferIndoorChanged(false);
            }
          },
          delay: const Duration(milliseconds: 300),
        ),

        const SizedBox(height: AppSpacing.sm),

        _ConstraintCard(
          icon: Icons.museum_outlined,
          title: 'Prefer indoor activities',
          description: 'More museums, galleries, and indoor attractions',
          value: preferIndoor,
          onChanged: (value) {
            onPreferIndoorChanged(value);
            if (value && preferOutdoor) {
              onPreferOutdoorChanged(false);
            }
          },
          delay: const Duration(milliseconds: 350),
        ),

        const SizedBox(height: AppSpacing.xl),

        // Optional note
        Container(
          padding: const EdgeInsets.all(AppSpacing.md),
          decoration: BoxDecoration(
            color: AppColors.surfaceVariant,
            borderRadius: BorderRadius.circular(AppSpacing.radiusMD),
          ),
          child: Row(
            children: [
              Icon(
                Icons.tips_and_updates_outlined,
                color: AppColors.accent,
                size: 20,
              ),
              const SizedBox(width: AppSpacing.sm),
              Expanded(
                child: Text(
                  'All constraints are optional. We\'ll do our best to accommodate your preferences while still creating a great itinerary.',
                  style: TextStyle(
                    fontSize: 12,
                    color: AppColors.textSecondary,
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
}

class _ConstraintCard extends StatelessWidget {
  final IconData icon;
  final String title;
  final String description;
  final bool value;
  final ValueChanged<bool> onChanged;
  final Duration delay;

  const _ConstraintCard({
    required this.icon,
    required this.title,
    required this.description,
    required this.value,
    required this.onChanged,
    required this.delay,
  });

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: () => onChanged(!value),
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 200),
        padding: const EdgeInsets.all(AppSpacing.md),
        decoration: BoxDecoration(
          color: value
              ? AppColors.accent.withOpacity(0.1)
              : AppColors.surface,
          borderRadius: BorderRadius.circular(AppSpacing.radiusMD),
          border: Border.all(
            color: value ? AppColors.accent : AppColors.border,
            width: value ? 2 : 1,
          ),
        ),
        child: Row(
          children: [
            Container(
              padding: const EdgeInsets.all(AppSpacing.sm),
              decoration: BoxDecoration(
                color: value
                    ? AppColors.accent.withOpacity(0.15)
                    : AppColors.surfaceVariant,
                borderRadius: BorderRadius.circular(AppSpacing.radiusSM),
              ),
              child: Icon(
                icon,
                color: value ? AppColors.accent : AppColors.textSecondary,
                size: 20,
              ),
            ),
            const SizedBox(width: AppSpacing.md),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    title,
                    style: TextStyle(
                      fontSize: 14,
                      fontWeight: FontWeight.w600,
                      color: value ? AppColors.accent : AppColors.textPrimary,
                    ),
                  ),
                  const SizedBox(height: 2),
                  Text(
                    description,
                    style: TextStyle(
                      fontSize: 12,
                      color: AppColors.textTertiary,
                    ),
                  ),
                ],
              ),
            ),
            Checkbox(
              value: value,
              onChanged: (v) => onChanged(v ?? false),
              activeColor: AppColors.accent,
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(4),
              ),
            ),
          ],
        ),
      ),
    ).animate(delay: delay).fadeIn().slideX(begin: 0.1);
  }
}
