import 'package:flutter/material.dart';

/// Application color palette
class AppColors {
  const AppColors._();

  // Brand Colors
  static const Color primary = Color(0xFF2D5A7B); // Deep ocean blue
  static const Color secondary = Color(0xFFE8A87C); // Warm coral/sunset
  static const Color accent = Color(0xFF41B3A3); // Teal/sea green

  // Primary variations
  static const Color primaryLight = Color(0xFF4A7A9B);
  static const Color primaryDark = Color(0xFF1A3D55);

  // Secondary variations
  static const Color secondaryLight = Color(0xFFF0C5A0);
  static const Color secondaryDark = Color(0xFFD08B58);

  // Accent variations
  static const Color accentLight = Color(0xFF6DD0C3);
  static const Color accentDark = Color(0xFF2E9183);

  // Group Type Colors
  static const Color family = Color(0xFF4CAF50);
  static const Color couple = Color(0xFFE91E63);
  static const Color solo = Color(0xFF2196F3);
  static const Color friends = Color(0xFFFF9800);
  static const Color business = Color(0xFF607D8B);
  static const Color extended = Color(0xFF9C27B0);

  // Vibe Colors
  static const Color cultural = Color(0xFF9B59B6);
  static const Color foodie = Color(0xFFE74C3C);
  static const Color romantic = Color(0xFFE91E63);
  static const Color adventure = Color(0xFFFF6B35);
  static const Color relaxation = Color(0xFF3498DB);
  static const Color nature = Color(0xFF27AE60);
  static const Color shopping = Color(0xFFF39C12);
  static const Color nightlife = Color(0xFF8E44AD);
  static const Color historical = Color(0xFF795548);
  static const Color artsy = Color(0xFFEC407A);

  // Neutral Colors
  static const Color white = Color(0xFFFFFFFF);
  static const Color black = Color(0xFF000000);
  static const Color background = Color(0xFFF8FAFB);
  static const Color surface = Color(0xFFFFFFFF);
  static const Color surfaceVariant = Color(0xFFF0F4F8);

  // Text Colors
  static const Color textPrimary = Color(0xFF1A1A2E);
  static const Color textSecondary = Color(0xFF4A5568);
  static const Color textTertiary = Color(0xFF718096);
  static const Color textDisabled = Color(0xFFA0AEC0);
  static const Color textOnPrimary = Color(0xFFFFFFFF);
  static const Color textOnSecondary = Color(0xFF1A1A2E);

  // Border Colors
  static const Color border = Color(0xFFE2E8F0);
  static const Color borderLight = Color(0xFFF1F5F9);
  static const Color borderFocused = primary;

  // Status Colors
  static const Color success = Color(0xFF22C55E);
  static const Color warning = Color(0xFFF59E0B);
  static const Color error = Color(0xFFEF4444);
  static const Color info = Color(0xFF3B82F6);

  // Shadow Colors
  static const Color shadowLight = Color(0x0A000000);
  static const Color shadowMedium = Color(0x14000000);
  static const Color shadowDark = Color(0x29000000);

  // Overlay Colors
  static const Color overlay = Color(0x80000000);
  static const Color overlayLight = Color(0x40000000);

  // Dark Theme Colors
  static const Color darkBackground = Color(0xFF0F172A);
  static const Color darkSurface = Color(0xFF1E293B);
  static const Color darkSurfaceVariant = Color(0xFF334155);
  static const Color darkBorder = Color(0xFF475569);
  static const Color darkTextPrimary = Color(0xFFF8FAFC);
  static const Color darkTextSecondary = Color(0xFFCBD5E1);

  /// Get group type color
  static Color groupTypeColor(String groupType) {
    return switch (groupType.toLowerCase()) {
      'family' => family,
      'couple' => couple,
      'solo' => solo,
      'friends' => friends,
      'business' => business,
      'extended' => extended,
      _ => primary,
    };
  }

  /// Get vibe color
  static Color vibeColor(String vibe) {
    return switch (vibe.toLowerCase()) {
      'cultural' => cultural,
      'foodie' => foodie,
      'romantic' => romantic,
      'adventure' => adventure,
      'relaxation' => relaxation,
      'nature' => nature,
      'shopping' => shopping,
      'nightlife' => nightlife,
      'historical' => historical,
      'artsy' => artsy,
      _ => accent,
    };
  }
}
