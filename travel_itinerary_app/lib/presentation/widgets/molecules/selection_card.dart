import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';

import '../../../theme/colors/app_colors.dart';
import '../../../theme/spacing/app_spacing.dart';

/// Visual selection card for group type, etc.
class SelectionCard extends StatelessWidget {
  final String id;
  final String label;
  final String icon;
  final String? description;
  final bool isSelected;
  final VoidCallback? onTap;
  final Color? accentColor;

  const SelectionCard({
    super.key,
    required this.id,
    required this.label,
    required this.icon,
    this.description,
    this.isSelected = false,
    this.onTap,
    this.accentColor,
  });

  @override
  Widget build(BuildContext context) {
    final color = accentColor ?? AppColors.groupTypeColor(id);

    return GestureDetector(
      onTap: onTap,
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 200),
        curve: Curves.easeOutCubic,
        padding: const EdgeInsets.all(AppSpacing.md),
        decoration: BoxDecoration(
          color: isSelected ? AppColors.gold.withOpacity(0.08) : AppColors.surface,
          borderRadius: BorderRadius.circular(AppSpacing.radiusLG),
          border: Border.all(
            color: isSelected ? AppColors.gold : AppColors.borderLight,
            width: isSelected ? 2.5 : 1,
          ),
          boxShadow: isSelected
              ? [
                  BoxShadow(
                    color: AppColors.gold.withOpacity(0.18),
                    blurRadius: 12,
                    offset: const Offset(0, 4),
                  ),
                ]
              : [
                  BoxShadow(
                    color: AppColors.shadowLight,
                    blurRadius: 6,
                    offset: const Offset(0, 2),
                  ),
                ],
        ),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            // Icon
            AnimatedContainer(
              duration: const Duration(milliseconds: 200),
              padding: const EdgeInsets.all(AppSpacing.sm),
              decoration: BoxDecoration(
                color: isSelected ? AppColors.gold.withOpacity(0.15) : AppColors.surfaceWarm,
                shape: BoxShape.circle,
              ),
              child: Text(
                icon,
                style: TextStyle(
                  fontSize: isSelected ? 32 : 28,
                ),
              ),
            ),
            const SizedBox(height: AppSpacing.sm),

            // Label
            Text(
              label,
              style: TextStyle(
                fontSize: 14,
                fontWeight: isSelected ? FontWeight.w600 : FontWeight.w500,
                color: isSelected ? AppColors.primary : AppColors.textPrimary,
              ),
              textAlign: TextAlign.center,
            ),

            // Description
            if (description != null) ...[
              const SizedBox(height: AppSpacing.xs),
              Text(
                description!,
                style: TextStyle(
                  fontSize: 12,
                  color: AppColors.textTertiary,
                ),
                textAlign: TextAlign.center,
                maxLines: 2,
                overflow: TextOverflow.ellipsis,
              ),
            ],

            // Selection indicator
            if (isSelected) ...[
              const SizedBox(height: AppSpacing.sm),
              Icon(
                Icons.check_circle,
                color: AppColors.gold,
                size: 20,
              ),
            ],
          ],
        ),
      ),
    );
  }
}

/// Extension for animated selection card
extension SelectionCardAnimated on SelectionCard {
  Widget animated({
    Duration delay = Duration.zero,
    Duration duration = const Duration(milliseconds: 300),
  }) {
    return this
        .animate(delay: delay)
        .fadeIn(duration: duration)
        .scale(begin: const Offset(0.95, 0.95), duration: duration);
  }
}
