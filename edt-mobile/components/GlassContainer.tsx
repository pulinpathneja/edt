import React from 'react';
import { StyleSheet, ViewStyle, View, Platform } from 'react-native';
import { BlurView } from 'expo-blur';
import { Colors, Radius } from '@/theme';

interface Props {
  children: React.ReactNode;
  style?: ViewStyle;
  intensity?: number;
}

export function GlassContainer({ children, style, intensity = 60 }: Props) {
  // BlurView works best on iOS; fallback to semi-transparent bg on other platforms
  if (Platform.OS === 'ios') {
    return (
      <BlurView intensity={intensity} tint="light" style={[styles.container, style]}>
        {children}
      </BlurView>
    );
  }

  return (
    <View style={[styles.container, styles.fallback, style]}>
      {children}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    borderRadius: Radius.xl,
    overflow: 'hidden',
    borderWidth: 1,
    borderColor: 'rgba(226, 229, 236, 0.5)',
  },
  fallback: {
    backgroundColor: 'rgba(255, 255, 255, 0.85)',
  },
});
