import 'package:flutter/material.dart';

/// Application spacing system
class AppSpacing {
  const AppSpacing._();

  static const AppSpacing instance = AppSpacing._();

  // Base spacing values
  static const double xs = 4.0;
  static const double sm = 8.0;
  static const double md = 16.0;
  static const double lg = 24.0;
  static const double xl = 32.0;
  static const double xxl = 48.0;
  static const double xxxl = 64.0;

  // Additional common sizes
  static const double none = 0.0;
  static const double tiny = 2.0;

  // Padding helpers
  EdgeInsets get paddingXS => const EdgeInsets.all(xs);
  EdgeInsets get paddingSM => const EdgeInsets.all(sm);
  EdgeInsets get paddingMD => const EdgeInsets.all(md);
  EdgeInsets get paddingLG => const EdgeInsets.all(lg);
  EdgeInsets get paddingXL => const EdgeInsets.all(xl);
  EdgeInsets get paddingXXL => const EdgeInsets.all(xxl);

  // Horizontal padding
  EdgeInsets get horizontalXS => const EdgeInsets.symmetric(horizontal: xs);
  EdgeInsets get horizontalSM => const EdgeInsets.symmetric(horizontal: sm);
  EdgeInsets get horizontalMD => const EdgeInsets.symmetric(horizontal: md);
  EdgeInsets get horizontalLG => const EdgeInsets.symmetric(horizontal: lg);
  EdgeInsets get horizontalXL => const EdgeInsets.symmetric(horizontal: xl);

  // Vertical padding
  EdgeInsets get verticalXS => const EdgeInsets.symmetric(vertical: xs);
  EdgeInsets get verticalSM => const EdgeInsets.symmetric(vertical: sm);
  EdgeInsets get verticalMD => const EdgeInsets.symmetric(vertical: md);
  EdgeInsets get verticalLG => const EdgeInsets.symmetric(vertical: lg);
  EdgeInsets get verticalXL => const EdgeInsets.symmetric(vertical: xl);

  // Screen padding (for consistent page margins)
  EdgeInsets get screenPadding => const EdgeInsets.symmetric(
        horizontal: md,
        vertical: lg,
      );

  EdgeInsets get screenPaddingHorizontal => const EdgeInsets.symmetric(
        horizontal: md,
      );

  // Card padding
  EdgeInsets get cardPadding => const EdgeInsets.all(md);
  EdgeInsets get cardPaddingLarge => const EdgeInsets.all(lg);

  // List item padding
  EdgeInsets get listItemPadding => const EdgeInsets.symmetric(
        horizontal: md,
        vertical: sm,
      );

  // Button padding
  EdgeInsets get buttonPadding => const EdgeInsets.symmetric(
        horizontal: lg,
        vertical: md,
      );

  EdgeInsets get buttonPaddingSmall => const EdgeInsets.symmetric(
        horizontal: md,
        vertical: sm,
      );

  // Chip padding
  EdgeInsets get chipPadding => const EdgeInsets.symmetric(
        horizontal: sm,
        vertical: xs,
      );

  // Gap sizes (for use with SizedBox)
  SizedBox get gapXS => const SizedBox(width: xs, height: xs);
  SizedBox get gapSM => const SizedBox(width: sm, height: sm);
  SizedBox get gapMD => const SizedBox(width: md, height: md);
  SizedBox get gapLG => const SizedBox(width: lg, height: lg);
  SizedBox get gapXL => const SizedBox(width: xl, height: xl);
  SizedBox get gapXXL => const SizedBox(width: xxl, height: xxl);

  // Horizontal gaps
  SizedBox get horizontalGapXS => const SizedBox(width: xs);
  SizedBox get horizontalGapSM => const SizedBox(width: sm);
  SizedBox get horizontalGapMD => const SizedBox(width: md);
  SizedBox get horizontalGapLG => const SizedBox(width: lg);
  SizedBox get horizontalGapXL => const SizedBox(width: xl);

  // Vertical gaps
  SizedBox get verticalGapXS => const SizedBox(height: xs);
  SizedBox get verticalGapSM => const SizedBox(height: sm);
  SizedBox get verticalGapMD => const SizedBox(height: md);
  SizedBox get verticalGapLG => const SizedBox(height: lg);
  SizedBox get verticalGapXL => const SizedBox(height: xl);
  SizedBox get verticalGapXXL => const SizedBox(height: xxl);

  // Border radius
  static const double radiusXS = 4.0;
  static const double radiusSM = 8.0;
  static const double radiusMD = 12.0;
  static const double radiusLG = 16.0;
  static const double radiusXL = 24.0;
  static const double radiusFull = 999.0;

  BorderRadius get borderRadiusXS => BorderRadius.circular(radiusXS);
  BorderRadius get borderRadiusSM => BorderRadius.circular(radiusSM);
  BorderRadius get borderRadiusMD => BorderRadius.circular(radiusMD);
  BorderRadius get borderRadiusLG => BorderRadius.circular(radiusLG);
  BorderRadius get borderRadiusXL => BorderRadius.circular(radiusXL);
  BorderRadius get borderRadiusFull => BorderRadius.circular(radiusFull);
}
