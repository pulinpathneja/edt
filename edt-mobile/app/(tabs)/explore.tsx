import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import { Ionicons } from '@expo/vector-icons';
import { Colors, Typography, Spacing } from '@/theme';

export default function ExploreScreen() {
  const insets = useSafeAreaInsets();

  return (
    <View style={[styles.container, { paddingTop: insets.top + Spacing.lg }]}>
      <Ionicons name="compass-outline" size={48} color={Colors.textTertiary} />
      <Text style={[Typography.titleMedium, { marginTop: Spacing.md }]}>Explore</Text>
      <Text style={[Typography.bodySmall, { textAlign: 'center', marginTop: Spacing.xs }]}>
        Discover destinations, routes, and travel inspiration
      </Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: Colors.background,
    alignItems: 'center',
    justifyContent: 'center',
    paddingHorizontal: Spacing.xl,
  },
});
