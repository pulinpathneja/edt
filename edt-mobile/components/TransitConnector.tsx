import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { Colors, Typography, Spacing, Radius } from '@/theme';
import type { TransitInfo } from '@/types';

const MODE_CONFIG: Record<string, { icon: keyof typeof Ionicons.glyphMap; color: string; label: string }> = {
  walk: { icon: 'walk-outline', color: Colors.textTertiary, label: 'Walk' },
  train: { icon: 'train-outline', color: Colors.activityTransport, label: 'Train' },
  car: { icon: 'car-outline', color: Colors.textSecondary, label: 'Drive' },
  bus: { icon: 'bus-outline', color: Colors.warning, label: 'Bus' },
};

interface Props {
  transit: TransitInfo;
}

export function TransitConnector({ transit }: Props) {
  const config = MODE_CONFIG[transit.mode] ?? MODE_CONFIG.walk;

  return (
    <View style={styles.container}>
      {/* Dashed line connecting to timeline */}
      <View style={styles.dashLine}>
        {Array.from({ length: 4 }, (_, i) => (
          <View key={i} style={styles.dash} />
        ))}
      </View>

      <View style={styles.content}>
        <View style={[styles.iconBox, { backgroundColor: config.color + '1A' }]}>
          <Ionicons name={config.icon} size={14} color={config.color} />
        </View>
        <Text style={styles.text}>
          {transit.duration} {config.label}
          {transit.note ? ` \u00B7 ${transit.note}` : ''}
        </Text>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    paddingLeft: 48,
    paddingVertical: Spacing.xxs,
  },
  dashLine: {
    position: 'absolute',
    left: 37,
    top: 0,
    bottom: 0,
    width: 2,
    alignItems: 'center',
    justifyContent: 'space-evenly',
  },
  dash: {
    width: 2,
    height: 4,
    backgroundColor: Colors.timelineLine,
    borderRadius: 1,
  },
  content: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: Spacing.xs,
    marginLeft: Spacing.xxs,
  },
  iconBox: {
    width: 28,
    height: 28,
    borderRadius: Radius.sm,
    alignItems: 'center',
    justifyContent: 'center',
  },
  text: {
    ...Typography.caption,
    color: Colors.textSecondary,
  },
});
