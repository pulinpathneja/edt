import React from 'react';
import { View, StyleSheet } from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { Colors, Spacing, Radius } from '@/theme';

interface Props {
  steps: number;
  current: number;
}

export function StepIndicator({ steps, current }: Props) {
  return (
    <View style={styles.container}>
      {Array.from({ length: steps }, (_, i) => (
        <View key={i} style={styles.stepWrapper}>
          {i <= current ? (
            <LinearGradient
              colors={[Colors.primary, Colors.primaryLight]}
              start={{ x: 0, y: 0 }}
              end={{ x: 1, y: 0 }}
              style={styles.step}
            />
          ) : (
            <View style={[styles.step, styles.stepInactive]} />
          )}
        </View>
      ))}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flexDirection: 'row',
    gap: Spacing.xxs,
    paddingHorizontal: Spacing.md,
    marginBottom: Spacing.lg,
  },
  stepWrapper: {
    flex: 1,
    height: 4,
    borderRadius: Radius.full,
    overflow: 'hidden',
  },
  step: {
    flex: 1,
    borderRadius: Radius.full,
  },
  stepInactive: {
    backgroundColor: Colors.surfaceVariant,
  },
});
