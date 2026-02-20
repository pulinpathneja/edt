import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

import '../colors/app_colors.dart';

/// Modern typography system using Plus Jakarta Sans
/// (matching edt-ui/modular-joy-maker design system)
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
  static const FontWeight extraBold = FontWeight.w800;

  // Helper for heading styles
  static TextStyle _heading({
    double fontSize = 16,
    FontWeight fontWeight = FontWeight.w700,
    double height = 1.25,
    double letterSpacing = 0,
    Color color = AppColors.textPrimary,
  }) {
    return GoogleFonts.plusJakartaSans(
      fontSize: fontSize,
      fontWeight: fontWeight,
      height: height,
      letterSpacing: letterSpacing,
      color: color,
    );
  }

  // Helper for body styles
  static TextStyle _body({
    double fontSize = 14,
    FontWeight fontWeight = FontWeight.w400,
    double height = 1.5,
    double letterSpacing = 0,
    Color color = AppColors.textPrimary,
  }) {
    return GoogleFonts.plusJakartaSans(
      fontSize: fontSize,
      fontWeight: fontWeight,
      height: height,
      letterSpacing: letterSpacing,
      color: color,
    );
  }

  // Display Styles
  TextStyle get displayLarge => _heading(
        fontSize: 57,
        fontWeight: extraBold,
        height: 1.12,
        letterSpacing: -0.25,
      );

  TextStyle get displayMedium => _heading(
        fontSize: 45,
        fontWeight: extraBold,
        height: 1.16,
      );

  TextStyle get displaySmall => _heading(
        fontSize: 36,
        fontWeight: bold,
        height: 1.22,
      );

  // Headline Styles
  TextStyle get headlineLarge => _heading(
        fontSize: 32,
        fontWeight: bold,
        height: 1.25,
      );

  TextStyle get headlineMedium => _heading(
        fontSize: 28,
        fontWeight: bold,
        height: 1.29,
      );

  TextStyle get headlineSmall => _heading(
        fontSize: 24,
        fontWeight: semiBold,
        height: 1.33,
      );

  // Title Styles
  TextStyle get titleLarge => _body(
        fontSize: 22,
        fontWeight: semiBold,
        height: 1.27,
      );

  TextStyle get titleMedium => _body(
        fontSize: 18,
        fontWeight: medium,
        height: 1.33,
        letterSpacing: 0.15,
      );

  TextStyle get titleSmall => _body(
        fontSize: 16,
        fontWeight: medium,
        height: 1.43,
        letterSpacing: 0.1,
      );

  // Body Styles
  TextStyle get bodyLarge => _body(
        fontSize: 16,
        fontWeight: regular,
        height: 1.5,
        letterSpacing: 0.5,
      );

  TextStyle get bodyMedium => _body(
        fontSize: 14,
        fontWeight: regular,
        height: 1.43,
        letterSpacing: 0.25,
      );

  TextStyle get bodySmall => _body(
        fontSize: 12,
        fontWeight: regular,
        height: 1.33,
        letterSpacing: 0.4,
        color: AppColors.textSecondary,
      );

  // Label Styles
  TextStyle get labelLarge => _body(
        fontSize: 14,
        fontWeight: medium,
        height: 1.43,
        letterSpacing: 0.1,
      );

  TextStyle get labelMedium => _body(
        fontSize: 12,
        fontWeight: medium,
        height: 1.33,
        letterSpacing: 0.5,
        color: AppColors.textSecondary,
      );

  TextStyle get labelSmall => _body(
        fontSize: 11,
        fontWeight: medium,
        height: 1.45,
        letterSpacing: 0.5,
        color: AppColors.textTertiary,
      );

  // Button Text
  TextStyle get button => _body(
        fontSize: 14,
        fontWeight: semiBold,
        height: 1.43,
        letterSpacing: 0.1,
        color: AppColors.textOnPrimary,
      );

  // Caption
  TextStyle get caption => _body(
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
