import 'package:flutter/material.dart';

/// Design system colors (from edt-ui/modular-joy-maker CSS custom properties)
class AppColors {
  const AppColors();
  const AppColors._();

  // Brand Colors — from --primary, --primary-glow
  static const Color primary = Color(0xFF2563EB); // HSL(221,83%,53%)
  static const Color primaryDark = Color(0xFF1A4FC9); // HSL(221,83%,45%) --secondary-foreground
  static const Color primaryLight = Color(0xFF4F6EF5); // HSL(230,90%,62%) --primary-glow
  static const Color secondary = Color(0xFFEEF2FD); // HSL(221,70%,96%) --secondary
  static const Color accent = Color(0xFFEEF2FD); // --accent (same as secondary)
  static const Color accentForeground = Color(0xFF1A4FC9); // --accent-foreground

  // Aliases (used throughout screens as accent)
  static const Color gold = primary;
  static const Color goldLight = Color(0xFFBFDBFE); // Tailwind blue-200

  // Backgrounds — from --background, --card, --muted
  static const Color background = Color(0xFFF4F5F8); // HSL(220,20%,97%) --background
  static const Color surface = Color(0xFFFFFFFF); // --card
  static const Color surfaceVariant = Color(0xFFECEEF2); // HSL(220,14%,94%) --muted
  static const Color surfaceWarm = Color(0xFFEEF2FD); // --secondary

  // Text Colors — from --foreground, --muted-foreground
  static const Color textPrimary = Color(0xFF0D1526); // HSL(222,47%,11%) --foreground
  static const Color textSecondary = Color(0xFF6B7280); // HSL(220,9%,46%) --muted-foreground
  static const Color textTertiary = Color(0xFF94A3B8); // Slate-400
  static const Color textDisabled = Color(0xFFCBD5E1); // Slate-300
  static const Color textOnPrimary = Color(0xFFFFFFFF); // --primary-foreground
  static const Color textOnSecondary = Color(0xFF1A4FC9); // --secondary-foreground

  // Border Colors — from --border, --input
  static const Color border = Color(0xFFE2E5EC); // HSL(220,13%,91%) --border
  static const Color borderLight = Color(0xFFF1F5F9); // Slate-100
  static const Color borderFocused = primary; // --ring

  // Status Colors — from --success, --destructive
  static const Color success = Color(0xFF1E8F5B); // HSL(152,69%,40%) --success
  static const Color warning = Color(0xFFF59E0B); // Amber-500
  static const Color error = Color(0xFFEF3B3B); // HSL(0,84%,60%) --destructive
  static const Color info = Color(0xFF2563EB); // Primary blue

  // Timeline Colors — from --timeline-*
  static const Color timelineLine = Color(0xFFD5D9E2); // HSL(220,14%,88%)
  static const Color timelineDot = Color(0xFF2563EB); // --timeline-dot (primary)
  static const Color timelineDotMuted = Color(0xFFBCC2CF); // HSL(220,10%,78%)

  // Shadow Colors
  static const Color shadowLight = Color(0x0F64748B);
  static const Color shadowMedium = Color(0x1A64748B);
  static const Color shadowDark = Color(0x2964748B);

  // Overlay Colors
  static const Color overlay = Color(0x800D1526);
  static const Color overlayLight = Color(0x400D1526);

  // White & Black
  static const Color white = Color(0xFFFFFFFF);
  static const Color black = Color(0xFF000000);

  // Group Type Colors
  static const Color family = Color(0xFF4A7C59);
  static const Color couple = Color(0xFFC44536);
  static const Color solo = Color(0xFF5B8DA0);
  static const Color friends = Color(0xFFD4A04A);
  static const Color business = Color(0xFF7A6B5D);
  static const Color extended = Color(0xFF2563EB);

  // Vibe Colors
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

  // Activity Type Colors (matching modular-joy-maker Tailwind palette)
  static const Color activityHotel = Color(0xFFF59E0B); // Amber-500
  static const Color activityMeal = Color(0xFFF43F5E); // Rose-500
  static const Color activityTransport = Color(0xFF3B82F6); // Blue-500
  static const Color activitySightseeing = Color(0xFF10B981); // Emerald-500
  static const Color activityShopping = Color(0xFF8B5CF6); // Violet-500

  // Activity Type Light Backgrounds (Tailwind *-50)
  static const Color activityHotelBg = Color(0xFFFFFBEB); // Amber-50
  static const Color activityMealBg = Color(0xFFFFF1F2); // Rose-50
  static const Color activityTransportBg = Color(0xFFEFF6FF); // Blue-50
  static const Color activitySightseeingBg = Color(0xFFECFDF5); // Emerald-50
  static const Color activityShoppingBg = Color(0xFFF5F3FF); // Violet-50

  // Activity Type Border Colors (Tailwind *-200)
  static const Color activityHotelBorder = Color(0xFFFDE68A); // Amber-200
  static const Color activityMealBorder = Color(0xFFFECDD3); // Rose-200
  static const Color activityTransportBorder = Color(0xFFBFDBFE); // Blue-200
  static const Color activitySightseeingBorder = Color(0xFFA7F3D0); // Emerald-200
  static const Color activityShoppingBorder = Color(0xFFDDD6FE); // Violet-200

  // Dark Theme Colors — from dark mode CSS overrides
  static const Color darkBackground = Color(0xFF090D16); // HSL(224,30%,7%)
  static const Color darkSurface = Color(0xFF131A26); // HSL(224,22%,12%)
  static const Color darkSurfaceVariant = Color(0xFF202737); // HSL(224,16%,18%) --muted dark
  static const Color darkSecondary = Color(0xFF1C2336); // HSL(224,20%,16%) --secondary dark
  static const Color darkBorder = Color(0xFF2A3347); // HSL(224,14%,22%)
  static const Color darkTextPrimary = Color(0xFFE2E8F0); // HSL(210,20%,92%)
  static const Color darkTextSecondary = Color(0xFF858FA3); // HSL(220,10%,58%)
  static const Color darkPrimary = Color(0xFF3B6EF0); // HSL(221,83%,58%)
  static const Color darkPrimaryGlow = Color(0xFF5A76F7); // HSL(230,90%,65%)
  static const Color darkSuccess = Color(0xFF2DA86B); // HSL(152,60%,45%)

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
      _ => primary,
    };
  }
}
