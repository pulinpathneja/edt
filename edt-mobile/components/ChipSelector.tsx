import React from 'react';
import { View, Text, Pressable, StyleSheet } from 'react-native';
import { Colors, Typography, Spacing, Radius } from '@/theme';

interface Props {
  options: string[];
  selected: string[];
  onToggle: (value: string) => void;
  max?: number;
  colorMap?: (value: string) => string;
}

export function ChipSelector({ options, selected, onToggle, max, colorMap }: Props) {
  return (
    <View style={styles.container}>
      {options.map((option) => {
        const isSelected = selected.includes(option);
        const accent = colorMap?.(option) ?? Colors.primary;
        const disabled = !isSelected && max != null && selected.length >= max;

        return (
          <Pressable
            key={option}
            onPress={() => !disabled && onToggle(option)}
            style={[
              styles.chip,
              isSelected && { backgroundColor: accent + '18', borderColor: accent },
              disabled && { opacity: 0.4 },
            ]}
          >
            <Text
              style={[
                Typography.labelLarge,
                styles.chipText,
                isSelected && { color: accent },
              ]}
            >
              {option.charAt(0).toUpperCase() + option.slice(1)}
            </Text>
          </Pressable>
        );
      })}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: Spacing.xs,
  },
  chip: {
    paddingHorizontal: Spacing.md,
    paddingVertical: Spacing.xs,
    borderRadius: Radius.full,
    borderWidth: 1.5,
    borderColor: Colors.border,
    backgroundColor: Colors.surface,
  },
  chipText: {
    color: Colors.textSecondary,
  },
});
