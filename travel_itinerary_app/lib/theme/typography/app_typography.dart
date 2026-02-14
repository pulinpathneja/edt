import 'package:flutter/material.dart';

import '../colors/app_colors.dart';

/// Application typography system
class AppTypography {
  const AppTypography._();

  static const AppTypography instance = AppTypography._();

  // Use system font as fallback, replace with 'Poppins' after adding font files
  static const String? fontFamily = null;

  // Font Weights
  static const FontWeight regular = FontWeight.w400;
  static const FontWeight medium = FontWeight.w500;
  static const FontWeight semiBold = FontWeight.w600;
  static const FontWeight bold = FontWeight.w700;

  // Display Styles (36-57px)
  TextStyle get displayLarge => const TextStyle(
        fontFamily: fontFamily,
        fontSize: 57,
        fontWeight: bold,
        height: 1.12,
        letterSpacing: -0.25,
        color: AppColors.textPrimary,
      );

  TextStyle get displayMedium => const TextStyle(
        fontFamily: fontFamily,
        fontSize: 45,
        fontWeight: bold,
        height: 1.16,
        letterSpacing: 0,
        color: AppColors.textPrimary,
      );

  TextStyle get displaySmall => const TextStyle(
        fontFamily: fontFamily,
        fontSize: 36,
        fontWeight: semiBold,
        height: 1.22,
        letterSpacing: 0,
        color: AppColors.textPrimary,
      );

  // Headline Styles (24-32px)
  TextStyle get headlineLarge => const TextStyle(
        fontFamily: fontFamily,
        fontSize: 32,
        fontWeight: semiBold,
        height: 1.25,
        letterSpacing: 0,
        color: AppColors.textPrimary,
      );

  TextStyle get headlineMedium => const TextStyle(
        fontFamily: fontFamily,
        fontSize: 28,
        fontWeight: semiBold,
        height: 1.29,
        letterSpacing: 0,
        color: AppColors.textPrimary,
      );

  TextStyle get headlineSmall => const TextStyle(
        fontFamily: fontFamily,
        fontSize: 24,
        fontWeight: semiBold,
        height: 1.33,
        letterSpacing: 0,
        color: AppColors.textPrimary,
      );

  // Title Styles (18-22px)
  TextStyle get titleLarge => const TextStyle(
        fontFamily: fontFamily,
        fontSize: 22,
        fontWeight: semiBold,
        height: 1.27,
        letterSpacing: 0,
        color: AppColors.textPrimary,
      );

  TextStyle get titleMedium => const TextStyle(
        fontFamily: fontFamily,
        fontSize: 18,
        fontWeight: medium,
        height: 1.33,
        letterSpacing: 0.15,
        color: AppColors.textPrimary,
      );

  TextStyle get titleSmall => const TextStyle(
        fontFamily: fontFamily,
        fontSize: 16,
        fontWeight: medium,
        height: 1.43,
        letterSpacing: 0.1,
        color: AppColors.textPrimary,
      );

  // Body Styles (14-16px)
  TextStyle get bodyLarge => const TextStyle(
        fontFamily: fontFamily,
        fontSize: 16,
        fontWeight: regular,
        height: 1.5,
        letterSpacing: 0.5,
        color: AppColors.textPrimary,
      );

  TextStyle get bodyMedium => const TextStyle(
        fontFamily: fontFamily,
        fontSize: 14,
        fontWeight: regular,
        height: 1.43,
        letterSpacing: 0.25,
        color: AppColors.textPrimary,
      );

  TextStyle get bodySmall => const TextStyle(
        fontFamily: fontFamily,
        fontSize: 12,
        fontWeight: regular,
        height: 1.33,
        letterSpacing: 0.4,
        color: AppColors.textSecondary,
      );

  // Label Styles (11-14px)
  TextStyle get labelLarge => const TextStyle(
        fontFamily: fontFamily,
        fontSize: 14,
        fontWeight: medium,
        height: 1.43,
        letterSpacing: 0.1,
        color: AppColors.textPrimary,
      );

  TextStyle get labelMedium => const TextStyle(
        fontFamily: fontFamily,
        fontSize: 12,
        fontWeight: medium,
        height: 1.33,
        letterSpacing: 0.5,
        color: AppColors.textSecondary,
      );

  TextStyle get labelSmall => const TextStyle(
        fontFamily: fontFamily,
        fontSize: 11,
        fontWeight: medium,
        height: 1.45,
        letterSpacing: 0.5,
        color: AppColors.textTertiary,
      );

  // Button Text
  TextStyle get button => const TextStyle(
        fontFamily: fontFamily,
        fontSize: 14,
        fontWeight: semiBold,
        height: 1.43,
        letterSpacing: 0.1,
        color: AppColors.textOnPrimary,
      );

  // Caption
  TextStyle get caption => const TextStyle(
        fontFamily: fontFamily,
        fontSize: 12,
        fontWeight: regular,
        height: 1.33,
        letterSpacing: 0.4,
        color: AppColors.textTertiary,
      );

  /// Convert to Flutter TextTheme
  TextTheme toTextTheme() {
    return TextTheme(
      displayLarge: displayLarge,
      displayMedium: displayMedium,
      displaySmall: displaySmall,
      headlineLarge: headlineLarge,
      headlineMedium: headlineMedium,
      headlineSmall: headlineSmall,
      titleLarge: titleLarge,
      titleMedium: titleMedium,
      titleSmall: titleSmall,
      bodyLarge: bodyLarge,
      bodyMedium: bodyMedium,
      bodySmall: bodySmall,
      labelLarge: labelLarge,
      labelMedium: labelMedium,
      labelSmall: labelSmall,
    );
  }
}
