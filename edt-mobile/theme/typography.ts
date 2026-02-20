import { TextStyle } from 'react-native';
import { Colors } from './colors';

/**
 * Typography system matching Plus Jakarta Sans styles from Flutter and modular-joy-maker.
 */

export const FontWeights = {
  regular: '400' as const,
  medium: '500' as const,
  semiBold: '600' as const,
  bold: '700' as const,
  extraBold: '800' as const,
};

export const Typography = {
  // Display
  displayLarge: {
    fontFamily: 'PlusJakartaSans_800ExtraBold',
    fontSize: 57,
    lineHeight: 57 * 1.12,
    letterSpacing: -0.25,
    color: Colors.textPrimary,
  } as TextStyle,
  displayMedium: {
    fontFamily: 'PlusJakartaSans_800ExtraBold',
    fontSize: 45,
    lineHeight: 45 * 1.16,
    color: Colors.textPrimary,
  } as TextStyle,
  displaySmall: {
    fontFamily: 'PlusJakartaSans_700Bold',
    fontSize: 36,
    lineHeight: 36 * 1.22,
    color: Colors.textPrimary,
  } as TextStyle,

  // Headline
  headlineLarge: {
    fontFamily: 'PlusJakartaSans_700Bold',
    fontSize: 32,
    lineHeight: 32 * 1.25,
    color: Colors.textPrimary,
  } as TextStyle,
  headlineMedium: {
    fontFamily: 'PlusJakartaSans_700Bold',
    fontSize: 28,
    lineHeight: 28 * 1.29,
    color: Colors.textPrimary,
  } as TextStyle,
  headlineSmall: {
    fontFamily: 'PlusJakartaSans_600SemiBold',
    fontSize: 24,
    lineHeight: 24 * 1.33,
    color: Colors.textPrimary,
  } as TextStyle,

  // Title
  titleLarge: {
    fontFamily: 'PlusJakartaSans_600SemiBold',
    fontSize: 22,
    lineHeight: 22 * 1.27,
    color: Colors.textPrimary,
  } as TextStyle,
  titleMedium: {
    fontFamily: 'PlusJakartaSans_500Medium',
    fontSize: 18,
    lineHeight: 18 * 1.33,
    letterSpacing: 0.15,
    color: Colors.textPrimary,
  } as TextStyle,
  titleSmall: {
    fontFamily: 'PlusJakartaSans_500Medium',
    fontSize: 16,
    lineHeight: 16 * 1.43,
    letterSpacing: 0.1,
    color: Colors.textPrimary,
  } as TextStyle,

  // Body
  bodyLarge: {
    fontFamily: 'PlusJakartaSans_400Regular',
    fontSize: 16,
    lineHeight: 16 * 1.5,
    letterSpacing: 0.5,
    color: Colors.textPrimary,
  } as TextStyle,
  bodyMedium: {
    fontFamily: 'PlusJakartaSans_400Regular',
    fontSize: 14,
    lineHeight: 14 * 1.43,
    letterSpacing: 0.25,
    color: Colors.textPrimary,
  } as TextStyle,
  bodySmall: {
    fontFamily: 'PlusJakartaSans_400Regular',
    fontSize: 12,
    lineHeight: 12 * 1.33,
    letterSpacing: 0.4,
    color: Colors.textSecondary,
  } as TextStyle,

  // Label
  labelLarge: {
    fontFamily: 'PlusJakartaSans_500Medium',
    fontSize: 14,
    lineHeight: 14 * 1.43,
    letterSpacing: 0.1,
    color: Colors.textPrimary,
  } as TextStyle,
  labelMedium: {
    fontFamily: 'PlusJakartaSans_500Medium',
    fontSize: 12,
    lineHeight: 12 * 1.33,
    letterSpacing: 0.5,
    color: Colors.textSecondary,
  } as TextStyle,
  labelSmall: {
    fontFamily: 'PlusJakartaSans_500Medium',
    fontSize: 11,
    lineHeight: 11 * 1.45,
    letterSpacing: 0.5,
    color: Colors.textTertiary,
  } as TextStyle,

  // Button
  button: {
    fontFamily: 'PlusJakartaSans_600SemiBold',
    fontSize: 14,
    lineHeight: 14 * 1.43,
    letterSpacing: 0.1,
    color: Colors.textOnPrimary,
  } as TextStyle,

  // Caption
  caption: {
    fontFamily: 'PlusJakartaSans_400Regular',
    fontSize: 12,
    lineHeight: 12 * 1.33,
    letterSpacing: 0.4,
    color: Colors.textTertiary,
  } as TextStyle,
} as const;
