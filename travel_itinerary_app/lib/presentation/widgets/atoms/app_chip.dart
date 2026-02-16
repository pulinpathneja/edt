import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';

import '../../../theme/colors/app_colors.dart';
import '../../../theme/spacing/app_spacing.dart';

/// Custom branded chip widget
class AppChip extends StatelessWidget {
  final String label;
  final String? icon;
  final bool isSelected;
  final VoidCallback? onTap;
  final Color? selectedColor;
  final bool showCheckmark;

  const AppChip({
    super.key,
    required this.label,
    this.icon,
    this.isSelected = false,
    this.onTap,
    this.selectedColor,
    this.showCheckmark = false,
  });

  @override
  Widget build(BuildContext context) {
    final effectiveColor = selectedColor ?? AppColors.primary;

    return GestureDetector(
      onTap: onTap,
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 200),
        curve: Curves.easeOutCubic,
        padding: const EdgeInsets.symmetric(
          horizontal: AppSpacing.md,
          vertical: AppSpacing.sm,
        ),
        decoration: BoxDecoration(
          color: isSelected
              ? effectiveColor.withOpacity(0.12)
              : AppColors.surfaceWarm,
          borderRadius: BorderRadius.circular(AppSpacing.radiusFull),
          border: Border.all(
            color: isSelected ? effectiveColor : AppColors.border,
            width: isSelected ? 2 : 1,
          ),
        ),
        child: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            if (showCheckmark && isSelected) ...[
              Icon(
                Icons.check,
                size: 16,
                color: effectiveColor,
              ),
              const SizedBox(width: AppSpacing.xs),
            ],
            if (icon != null) ...[
              Text(
                icon!,
                style: const TextStyle(fontSize: 16),
              ),
              const SizedBox(width: AppSpacing.xs),
            ],
            Text(
              label,
              style: TextStyle(
                fontSize: 14,
                fontWeight: isSelected ? FontWeight.w600 : FontWeight.w500,
                color: isSelected ? effectiveColor : AppColors.textPrimary,
              ),
            ),
          ],
        ),
      ),
    );
  }
}

/// Extension for animated chips
extension AppChipAnimated on AppChip {
  Widget animated({
    Duration delay = Duration.zero,
    Duration duration = const Duration(milliseconds: 200),
  }) {
    return this
        .animate(delay: delay)
        .fadeIn(duration: duration)
        .scale(begin: const Offset(0.9, 0.9), duration: duration);
  }
}
