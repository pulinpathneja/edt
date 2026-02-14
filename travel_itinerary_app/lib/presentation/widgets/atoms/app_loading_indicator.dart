import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';

import '../../../theme/colors/app_colors.dart';

/// Loading indicator size variants
enum LoadingIndicatorSize { small, medium, large }

/// Custom branded loading indicator
class AppLoadingIndicator extends StatelessWidget {
  final LoadingIndicatorSize size;
  final Color? color;
  final String? message;

  const AppLoadingIndicator({
    super.key,
    this.size = LoadingIndicatorSize.medium,
    this.color,
    this.message,
  });

  @override
  Widget build(BuildContext context) {
    return Column(
      mainAxisSize: MainAxisSize.min,
      children: [
        SizedBox(
          width: _getSize(),
          height: _getSize(),
          child: CircularProgressIndicator(
            strokeWidth: _getStrokeWidth(),
            valueColor: AlwaysStoppedAnimation<Color>(
              color ?? AppColors.primary,
            ),
          ),
        ),
        if (message != null) ...[
          const SizedBox(height: 16),
          Text(
            message!,
            style: TextStyle(
              fontSize: 14,
              color: AppColors.textSecondary,
            ),
            textAlign: TextAlign.center,
          )
              .animate(onPlay: (controller) => controller.repeat())
              .shimmer(duration: const Duration(seconds: 2)),
        ],
      ],
    );
  }

  double _getSize() {
    return switch (size) {
      LoadingIndicatorSize.small => 20,
      LoadingIndicatorSize.medium => 36,
      LoadingIndicatorSize.large => 48,
    };
  }

  double _getStrokeWidth() {
    return switch (size) {
      LoadingIndicatorSize.small => 2,
      LoadingIndicatorSize.medium => 3,
      LoadingIndicatorSize.large => 4,
    };
  }
}

/// Branded loading overlay
class AppLoadingOverlay extends StatelessWidget {
  final bool isLoading;
  final Widget child;
  final String? message;
  final Color? backgroundColor;

  const AppLoadingOverlay({
    super.key,
    required this.isLoading,
    required this.child,
    this.message,
    this.backgroundColor,
  });

  @override
  Widget build(BuildContext context) {
    return Stack(
      children: [
        child,
        if (isLoading)
          Positioned.fill(
            child: Container(
              color: backgroundColor ?? AppColors.overlay,
              child: Center(
                child: AppLoadingIndicator(
                  size: LoadingIndicatorSize.large,
                  message: message,
                  color: AppColors.white,
                ),
              ),
            ),
          ).animate().fadeIn(duration: const Duration(milliseconds: 200)),
      ],
    );
  }
}

/// Pulsing loading dots animation
class AppLoadingDots extends StatelessWidget {
  final Color? color;
  final double dotSize;

  const AppLoadingDots({
    super.key,
    this.color,
    this.dotSize = 8,
  });

  @override
  Widget build(BuildContext context) {
    final dotColor = color ?? AppColors.primary;

    return Row(
      mainAxisSize: MainAxisSize.min,
      children: List.generate(3, (index) {
        return Container(
          margin: EdgeInsets.symmetric(horizontal: dotSize / 2),
          child: _buildDot(dotColor, index),
        );
      }),
    );
  }

  Widget _buildDot(Color color, int index) {
    return Container(
      width: dotSize,
      height: dotSize,
      decoration: BoxDecoration(
        color: color,
        shape: BoxShape.circle,
      ),
    )
        .animate(
          onPlay: (controller) => controller.repeat(),
        )
        .scale(
          delay: Duration(milliseconds: index * 200),
          duration: const Duration(milliseconds: 600),
          begin: const Offset(1, 1),
          end: const Offset(1.3, 1.3),
        )
        .then()
        .scale(
          duration: const Duration(milliseconds: 600),
          begin: const Offset(1.3, 1.3),
          end: const Offset(1, 1),
        );
  }
}
