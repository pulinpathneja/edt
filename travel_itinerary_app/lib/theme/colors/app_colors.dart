import 'package:flutter/material.dart';

/// Warm + Premium color palette
class AppColors {
  const AppColors();
  const AppColors._();

  // Brand Colors - Warm & Premium
  static const Color primary = Color(0xFF8B6914); // Rich amber
  static const Color primaryDark = Color(0xFF5C4510); // Deep bronze
  static const Color primaryLight = Color(0xFFC49B38); // Light gold
  static const Color secondary = Color(0xFFD4A574); // Warm sand
  static const Color accent = Color(0xFF2C1810); // Espresso

  // Gold Accents
  static const Color gold = Color(0xFFC8A951); // Gold accents
  static const Color goldLight = Color(0xFFE8D5A0); // Light gold

  // Backgrounds
  static const Color background = Color(0xFFFEF9F2); // Warm cream
  static const Color surface = Color(0xFFFFFFFF); // White cards
  static const Color surfaceWarm = Color(0xFFFFF5E9); // Warm white
  static const Color surfaceVariant = Color(0xFFFFF0E0); // Warm surface

  // Text Colors
  static const Color textPrimary = Color(0xFF2C1810); // Dark espresso
  static const Color textSecondary = Color(0xFF7A6B5D); // Warm grey
  static const Color textTertiary = Color(0xFFA89888); // Light warm grey
  static const Color textDisabled = Color(0xFFC8B8A8); // Disabled warm
  static const Color textOnPrimary = Color(0xFFFFFFFF);
  static const Color textOnSecondary = Color(0xFF2C1810);

  // Border Colors
  static const Color border = Color(0xFFE8DDD0); // Warm border
  static const Color borderLight = Color(0xFFF5EDE2); // Light warm border
  static const Color borderFocused = gold;

  // Status Colors
  static const Color success = Color(0xFF4A7C59); // Forest green
  static const Color warning = Color(0xFFD4A04A); // Warm amber
  static const Color error = Color(0xFFC44536); // Warm red
  static const Color info = Color(0xFF5B8DA0); // Warm blue

  // Shadow Colors
  static const Color shadowLight = Color(0x0A3E2723); // Warm shadow
  static const Color shadowMedium = Color(0x143E2723);
  static const Color shadowDark = Color(0x293E2723);

  // Overlay Colors
  static const Color overlay = Color(0x802C1810);
  static const Color overlayLight = Color(0x402C1810);

  // White & Black
  static const Color white = Color(0xFFFFFFFF);
  static const Color black = Color(0xFF000000);

  // Group Type Colors - Warm palette
  static const Color family = Color(0xFF4A7C59);
  static const Color couple = Color(0xFFC44536);
  static const Color solo = Color(0xFF5B8DA0);
  static const Color friends = Color(0xFFD4A04A);
  static const Color business = Color(0xFF7A6B5D);
  static const Color extended = Color(0xFF8B6914);

  // Vibe Colors - Warm palette
  static const Color cultural = Color(0xFF8B6914);
  static const Color foodie = Color(0xFFC44536);
  static const Color romantic = Color(0xFFB85C5C);
  static const Color adventure = Color(0xFFCC7A3A);
  static const Color relaxation = Color(0xFF5B8DA0);
  static const Color nature = Color(0xFF4A7C59);
  static const Color shopping = Color(0xFFD4A04A);
  static const Color nightlife = Color(0xFF6B4E71);
  static const Color historical = Color(0xFF7A6B5D);
  static const Color artsy = Color(0xFFA0526B);

  // Dark Theme Colors
  static const Color darkBackground = Color(0xFF1A1210);
  static const Color darkSurface = Color(0xFF2C2420);
  static const Color darkSurfaceVariant = Color(0xFF3E3530);
  static const Color darkBorder = Color(0xFF5A4E48);
  static const Color darkTextPrimary = Color(0xFFFEF9F2);
  static const Color darkTextSecondary = Color(0xFFD4C4B4);

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
      _ => gold,
    };
  }
}
