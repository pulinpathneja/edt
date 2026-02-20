import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { activityTypeColors, Colors, Typography, Spacing, Radius } from '@/theme';
import type { ActivityData } from '@/types';

const TYPE_ICONS: Record<string, keyof typeof Ionicons.glyphMap> = {
  hotel: 'bed-outline',
  meal: 'restaurant-outline',
  transport: 'train-outline',
  sightseeing: 'camera-outline',
  shopping: 'bag-outline',
};

const TYPE_EMOJI: Record<string, string> = {
  hotel: '\u{1F3E8}',
  meal: '\u{1F37D}',
  transport: '\u{1F685}',
  sightseeing: '\u{1F4F8}',
  shopping: '\u{1F6CD}',
};

interface Props {
  data: ActivityData;
}

export function ActivityCard({ data }: Props) {
  const colors = activityTypeColors(data.type);
  const icon = TYPE_ICONS[data.type] ?? 'ellipse-outline';

  return (
    <View style={[styles.card, { backgroundColor: colors.bg, borderColor: colors.border }]}>
      <View style={styles.row}>
        <View style={[styles.iconBox, { backgroundColor: colors.border + '80' }]}>
          <Ionicons name={icon} size={20} color={colors.fg} />
        </View>
        <View style={styles.content}>
          <Text style={[Typography.labelLarge, { color: Colors.textPrimary }]} numberOfLines={1}>
            {data.title}
          </Text>
          {data.description ? (
            <Text style={[Typography.bodySmall, { color: Colors.textSecondary }]} numberOfLines={2}>
              {data.description}
            </Text>
          ) : null}
        </View>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  card: {
    borderRadius: Radius.lg,
    borderWidth: 1,
    padding: Spacing.sm,
  },
  row: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: Spacing.sm,
  },
  iconBox: {
    width: 44,
    height: 44,
    borderRadius: Radius.md,
    alignItems: 'center',
    justifyContent: 'center',
  },
  content: {
    flex: 1,
    gap: 2,
  },
});
