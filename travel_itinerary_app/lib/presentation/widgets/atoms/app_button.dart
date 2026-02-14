import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';

import '../../../theme/colors/app_colors.dart';
import '../../../theme/spacing/app_spacing.dart';

/// Button variants
enum AppButtonVariant { primary, secondary, outline, ghost }

/// Button sizes
enum AppButtonSize { small, medium, large }

/// Custom branded button widget
class AppButton extends StatelessWidget {
  final String label;
  final VoidCallback? onPressed;
  final AppButtonVariant variant;
  final AppButtonSize size;
  final IconData? leadingIcon;
  final IconData? trailingIcon;
  final bool isLoading;
  final bool isExpanded;
  final Color? customColor;

  const AppButton({
    super.key,
    required this.label,
    this.onPressed,
    this.variant = AppButtonVariant.primary,
    this.size = AppButtonSize.medium,
    this.leadingIcon,
    this.trailingIcon,
    this.isLoading = false,
    this.isExpanded = false,
    this.customColor,
  });

  @override
  Widget build(BuildContext context) {
    final isDisabled = onPressed == null || isLoading;

    return SizedBox(
      width: isExpanded ? double.infinity : null,
      height: _getHeight(),
      child: _buildButton(context, isDisabled),
    );
  }

  Widget _buildButton(BuildContext context, bool isDisabled) {
    final buttonStyle = _getButtonStyle(isDisabled);
    final child = _buildContent(isDisabled);

    switch (variant) {
      case AppButtonVariant.primary:
        return ElevatedButton(
          onPressed: isDisabled ? null : onPressed,
          style: buttonStyle,
          child: child,
        );
      case AppButtonVariant.secondary:
        return ElevatedButton(
          onPressed: isDisabled ? null : onPressed,
          style: buttonStyle,
          child: child,
        );
      case AppButtonVariant.outline:
        return OutlinedButton(
          onPressed: isDisabled ? null : onPressed,
          style: buttonStyle,
          child: child,
        );
      case AppButtonVariant.ghost:
        return TextButton(
          onPressed: isDisabled ? null : onPressed,
          style: buttonStyle,
          child: child,
        );
    }
  }

  Widget _buildContent(bool isDisabled) {
    if (isLoading) {
      return SizedBox(
        width: _getLoadingSize(),
        height: _getLoadingSize(),
        child: CircularProgressIndicator(
          strokeWidth: 2,
          valueColor: AlwaysStoppedAnimation<Color>(
            _getTextColor(isDisabled),
          ),
        ),
      );
    }

    final textStyle = TextStyle(
      fontSize: _getFontSize(),
      fontWeight: FontWeight.w600,
    );

    if (leadingIcon == null && trailingIcon == null) {
      return Text(label, style: textStyle);
    }

    return Row(
      mainAxisSize: MainAxisSize.min,
      mainAxisAlignment: MainAxisAlignment.center,
      children: [
        if (leadingIcon != null) ...[
          Icon(leadingIcon, size: _getIconSize()),
          SizedBox(width: AppSpacing.sm),
        ],
        Text(label, style: textStyle),
        if (trailingIcon != null) ...[
          SizedBox(width: AppSpacing.sm),
          Icon(trailingIcon, size: _getIconSize()),
        ],
      ],
    );
  }

  double _getHeight() {
    return switch (size) {
      AppButtonSize.small => 36,
      AppButtonSize.medium => 48,
      AppButtonSize.large => 56,
    };
  }

  double _getFontSize() {
    return switch (size) {
      AppButtonSize.small => 12,
      AppButtonSize.medium => 14,
      AppButtonSize.large => 16,
    };
  }

  double _getIconSize() {
    return switch (size) {
      AppButtonSize.small => 16,
      AppButtonSize.medium => 20,
      AppButtonSize.large => 24,
    };
  }

  double _getLoadingSize() {
    return switch (size) {
      AppButtonSize.small => 16,
      AppButtonSize.medium => 20,
      AppButtonSize.large => 24,
    };
  }

  EdgeInsets _getPadding() {
    return switch (size) {
      AppButtonSize.small => const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
      AppButtonSize.medium => const EdgeInsets.symmetric(horizontal: 20, vertical: 12),
      AppButtonSize.large => const EdgeInsets.symmetric(horizontal: 24, vertical: 16),
    };
  }

  Color _getBackgroundColor(bool isDisabled) {
    if (isDisabled) {
      return AppColors.surfaceVariant;
    }

    final baseColor = customColor ?? AppColors.primary;

    return switch (variant) {
      AppButtonVariant.primary => baseColor,
      AppButtonVariant.secondary => AppColors.secondary,
      AppButtonVariant.outline => Colors.transparent,
      AppButtonVariant.ghost => Colors.transparent,
    };
  }

  Color _getTextColor(bool isDisabled) {
    if (isDisabled) {
      return AppColors.textDisabled;
    }

    final baseColor = customColor ?? AppColors.primary;

    return switch (variant) {
      AppButtonVariant.primary => AppColors.textOnPrimary,
      AppButtonVariant.secondary => AppColors.textOnSecondary,
      AppButtonVariant.outline => baseColor,
      AppButtonVariant.ghost => baseColor,
    };
  }

  ButtonStyle _getButtonStyle(bool isDisabled) {
    return ButtonStyle(
      backgroundColor: WidgetStateProperty.all(_getBackgroundColor(isDisabled)),
      foregroundColor: WidgetStateProperty.all(_getTextColor(isDisabled)),
      padding: WidgetStateProperty.all(_getPadding()),
      elevation: WidgetStateProperty.all(0),
      shape: WidgetStateProperty.all(
        RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(AppSpacing.radiusMD),
          side: variant == AppButtonVariant.outline
              ? BorderSide(
                  color: isDisabled
                      ? AppColors.border
                      : (customColor ?? AppColors.primary),
                )
              : BorderSide.none,
        ),
      ),
    );
  }
}

/// Extension for animated buttons
extension AppButtonAnimated on AppButton {
  Widget animated({
    Duration delay = Duration.zero,
    Duration duration = const Duration(milliseconds: 300),
  }) {
    return this
        .animate(delay: delay)
        .fadeIn(duration: duration)
        .slideY(begin: 0.1, end: 0, duration: duration);
  }
}
