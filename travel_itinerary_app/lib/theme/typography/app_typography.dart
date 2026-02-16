import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

import '../colors/app_colors.dart';

/// Warm + Premium typography system
/// Headings: Playfair Display (elegant serif)
/// Body: Inter (clean sans-serif)
class AppTypography {
  const AppTypography._();

  static const AppTypography instance = AppTypography._();

  // Font families via google_fonts
  static String? fontFamily; // Set dynamically

  // Font Weights
  static const FontWeight regular = FontWeight.w400;
  static const FontWeight medium = FontWeight.w500;
  static const FontWeight semiBold = FontWeight.w600;
  static const FontWeight bold = FontWeight.w700;

  // Helper to get Playfair Display style
  static TextStyle _playfair({
    double fontSize = 16,
    FontWeight fontWeight = FontWeight.w600,
    double height = 1.25,
    double letterSpacing = 0,
    Color color = AppColors.textPrimary,
  }) {
    return GoogleFonts.playfairDisplay(
      fontSize: fontSize,
      fontWeight: fontWeight,
      height: height,
      letterSpacing: letterSpacing,
      color: color,
    );
  }

  // Helper to get Inter style
  static TextStyle _inter({
    double fontSize = 14,
    FontWeight fontWeight = FontWeight.w400,
    double height = 1.5,
    double letterSpacing = 0,
    Color color = AppColors.textPrimary,
  }) {
    return GoogleFonts.inter(
      fontSize: fontSize,
      fontWeight: fontWeight,
      height: height,
      letterSpacing: letterSpacing,
      color: color,
    );
  }

  // Display Styles - Playfair Display (elegant serif)
  TextStyle get displayLarge => _playfair(
        fontSize: 57,
        fontWeight: bold,
        height: 1.12,
        letterSpacing: -0.25,
      );

  TextStyle get displayMedium => _playfair(
        fontSize: 45,
        fontWeight: bold,
        height: 1.16,
      );

  TextStyle get displaySmall => _playfair(
        fontSize: 36,
        fontWeight: semiBold,
        height: 1.22,
      );

  // Headline Styles - Playfair Display
  TextStyle get headlineLarge => _playfair(
        fontSize: 32,
        fontWeight: semiBold,
        height: 1.25,
      );

  TextStyle get headlineMedium => _playfair(
        fontSize: 28,
        fontWeight: semiBold,
        height: 1.29,
      );

  TextStyle get headlineSmall => _playfair(
        fontSize: 24,
        fontWeight: semiBold,
        height: 1.33,
      );

  // Title Styles - Inter (clean transition)
  TextStyle get titleLarge => _inter(
        fontSize: 22,
        fontWeight: semiBold,
        height: 1.27,
      );

  TextStyle get titleMedium => _inter(
        fontSize: 18,
        fontWeight: medium,
        height: 1.33,
        letterSpacing: 0.15,
      );

  TextStyle get titleSmall => _inter(
        fontSize: 16,
        fontWeight: medium,
        height: 1.43,
        letterSpacing: 0.1,
      );

  // Body Styles - Inter
  TextStyle get bodyLarge => _inter(
        fontSize: 16,
        fontWeight: regular,
        height: 1.5,
        letterSpacing: 0.5,
      );

  TextStyle get bodyMedium => _inter(
        fontSize: 14,
        fontWeight: regular,
        height: 1.43,
        letterSpacing: 0.25,
      );

  TextStyle get bodySmall => _inter(
        fontSize: 12,
        fontWeight: regular,
        height: 1.33,
        letterSpacing: 0.4,
        color: AppColors.textSecondary,
      );

  // Label Styles - Inter
  TextStyle get labelLarge => _inter(
        fontSize: 14,
        fontWeight: medium,
        height: 1.43,
        letterSpacing: 0.1,
      );

  TextStyle get labelMedium => _inter(
        fontSize: 12,
        fontWeight: medium,
        height: 1.33,
        letterSpacing: 0.5,
        color: AppColors.textSecondary,
      );

  TextStyle get labelSmall => _inter(
        fontSize: 11,
        fontWeight: medium,
        height: 1.45,
        letterSpacing: 0.5,
        color: AppColors.textTertiary,
      );

  // Button Text - Inter
  TextStyle get button => _inter(
        fontSize: 14,
        fontWeight: semiBold,
        height: 1.43,
        letterSpacing: 0.1,
        color: AppColors.textOnPrimary,
      );

  // Caption - Inter
  TextStyle get caption => _inter(
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
