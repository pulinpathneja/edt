/**
 * Design system colors ported from travel_itinerary_app/lib/theme/colors/app_colors.dart
 * and edt-ui/modular-joy-maker CSS custom properties.
 */

export const Colors = {
  // Brand
  primary: '#2563EB',
  primaryDark: '#1A4FC9',
  primaryLight: '#4F6EF5',
  secondary: '#EEF2FD',
  accent: '#EEF2FD',
  accentForeground: '#1A4FC9',

  // Aliases
  gold: '#2563EB',
  goldLight: '#BFDBFE',

  // Backgrounds
  background: '#F4F5F8',
  surface: '#FFFFFF',
  surfaceVariant: '#ECEEF2',
  surfaceWarm: '#EEF2FD',

  // Text
  textPrimary: '#0D1526',
  textSecondary: '#6B7280',
  textTertiary: '#94A3B8',
  textDisabled: '#CBD5E1',
  textOnPrimary: '#FFFFFF',
  textOnSecondary: '#1A4FC9',

  // Border
  border: '#E2E5EC',
  borderLight: '#F1F5F9',
  borderFocused: '#2563EB',

  // Status
  success: '#1E8F5B',
  warning: '#F59E0B',
  error: '#EF3B3B',
  info: '#2563EB',

  // Timeline
  timelineLine: '#D5D9E2',
  timelineDot: '#2563EB',
  timelineDotMuted: '#BCC2CF',

  // Shadows
  shadowLight: 'rgba(100, 116, 139, 0.06)',
  shadowMedium: 'rgba(100, 116, 139, 0.10)',
  shadowDark: 'rgba(100, 116, 139, 0.16)',

  // Overlay
  overlay: 'rgba(13, 21, 38, 0.50)',
  overlayLight: 'rgba(13, 21, 38, 0.25)',

  // White & Black
  white: '#FFFFFF',
  black: '#000000',

  // Group Types
  groupFamily: '#4A7C59',
  groupCouple: '#C44536',
  groupSolo: '#5B8DA0',
  groupFriends: '#D4A04A',
  groupBusiness: '#7A6B5D',
  groupExtended: '#2563EB',

  // Vibes
  vibeCultural: '#8B6914',
  vibeFoodie: '#C44536',
  vibeRomantic: '#B85C5C',
  vibeAdventure: '#CC7A3A',
  vibeRelaxation: '#5B8DA0',
  vibeNature: '#4A7C59',
  vibeShopping: '#D4A04A',
  vibeNightlife: '#6B4E71',
  vibeHistorical: '#7A6B5D',
  vibeArtsy: '#A0526B',

  // Activity Types — foreground (icon/text)
  activityHotel: '#F59E0B',
  activityMeal: '#F43F5E',
  activityTransport: '#3B82F6',
  activitySightseeing: '#10B981',
  activityShopping: '#8B5CF6',

  // Activity Types — light backgrounds (*-50)
  activityHotelBg: '#FFFBEB',
  activityMealBg: '#FFF1F2',
  activityTransportBg: '#EFF6FF',
  activitySightseeingBg: '#ECFDF5',
  activityShoppingBg: '#F5F3FF',

  // Activity Types — border (*-200)
  activityHotelBorder: '#FDE68A',
  activityMealBorder: '#FECDD3',
  activityTransportBorder: '#BFDBFE',
  activitySightseeingBorder: '#A7F3D0',
  activityShoppingBorder: '#DDD6FE',

  // Dark Theme
  darkBackground: '#090D16',
  darkSurface: '#131A26',
  darkSurfaceVariant: '#202737',
  darkSecondary: '#1C2336',
  darkBorder: '#2A3347',
  darkTextPrimary: '#E2E8F0',
  darkTextSecondary: '#858FA3',
  darkPrimary: '#3B6EF0',
  darkPrimaryGlow: '#5A76F7',
  darkSuccess: '#2DA86B',
} as const;

/** Get color for a group type string */
export function groupTypeColor(groupType: string): string {
  const map: Record<string, string> = {
    family: Colors.groupFamily,
    couple: Colors.groupCouple,
    solo: Colors.groupSolo,
    friends: Colors.groupFriends,
    business: Colors.groupBusiness,
    extended: Colors.groupExtended,
  };
  return map[groupType.toLowerCase()] ?? Colors.primary;
}

/** Get color for a vibe string */
export function vibeColor(vibe: string): string {
  const map: Record<string, string> = {
    cultural: Colors.vibeCultural,
    foodie: Colors.vibeFoodie,
    romantic: Colors.vibeRomantic,
    adventure: Colors.vibeAdventure,
    relaxation: Colors.vibeRelaxation,
    nature: Colors.vibeNature,
    shopping: Colors.vibeShopping,
    nightlife: Colors.vibeNightlife,
    historical: Colors.vibeHistorical,
    artsy: Colors.vibeArtsy,
  };
  return map[vibe.toLowerCase()] ?? Colors.primary;
}

/** Activity type → { bg, border, fg } */
export function activityTypeColors(type: string) {
  const map: Record<string, { bg: string; border: string; fg: string }> = {
    hotel: { bg: Colors.activityHotelBg, border: Colors.activityHotelBorder, fg: Colors.activityHotel },
    meal: { bg: Colors.activityMealBg, border: Colors.activityMealBorder, fg: Colors.activityMeal },
    transport: { bg: Colors.activityTransportBg, border: Colors.activityTransportBorder, fg: Colors.activityTransport },
    sightseeing: { bg: Colors.activitySightseeingBg, border: Colors.activitySightseeingBorder, fg: Colors.activitySightseeing },
    shopping: { bg: Colors.activityShoppingBg, border: Colors.activityShoppingBorder, fg: Colors.activityShopping },
  };
  return map[type.toLowerCase()] ?? { bg: Colors.secondary, border: Colors.border, fg: Colors.primary };
}
