import React, { useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  Pressable,
  ActivityIndicator,
} from 'react-native';
import { useRouter } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import { LinearGradient } from 'expo-linear-gradient';
import { useCountryStore } from '@/stores/countryStore';
import { GradientButton } from '@/components/GradientButton';
import { MatchScoreCircle } from '@/components/MatchScoreCircle';
import { Colors, Typography, Spacing, Radius } from '@/theme';
import type { CityAllocationOption } from '@/types';

export default function AllocationOptionsScreen() {
  const router = useRouter();
  const insets = useSafeAreaInsets();
  const {
    allocationResponse, isLoadingAllocations,
    selectedAllocationIndex, selectAllocation,
    generateItinerary, isGenerating,
  } = useCountryStore();

  const handleGenerate = async () => {
    await generateItinerary();
    router.push('/country/itinerary');
  };

  if (isLoadingAllocations) {
    return (
      <View style={[styles.loadingContainer, { paddingTop: insets.top }]}>
        <ActivityIndicator size="large" color={Colors.primary} />
        <Text style={[Typography.titleSmall, { marginTop: Spacing.md }]}>
          Finding the best options...
        </Text>
      </View>
    );
  }

  if (!allocationResponse) {
    return (
      <View style={[styles.loadingContainer, { paddingTop: insets.top }]}>
        <Ionicons name="alert-circle-outline" size={48} color={Colors.error} />
        <Text style={[Typography.titleSmall, { marginTop: Spacing.md }]}>
          No allocation options available
        </Text>
        <Pressable onPress={() => router.back()} style={{ marginTop: Spacing.md }}>
          <Text style={[Typography.button, { color: Colors.primary }]}>Go Back</Text>
        </Pressable>
      </View>
    );
  }

  return (
    <View style={[styles.container, { paddingTop: insets.top }]}>
      {/* Header */}
      <View style={styles.header}>
        <Pressable onPress={() => router.back()} style={styles.backBtn}>
          <Ionicons name="arrow-back" size={22} color={Colors.textPrimary} />
        </Pressable>
        <View>
          <Text style={Typography.titleLarge}>Choose Your Plan</Text>
          <Text style={[Typography.bodySmall, { marginTop: 2 }]}>
            {allocationResponse.country_name} \u00B7 {allocationResponse.total_days} days
          </Text>
        </View>
      </View>

      <ScrollView
        contentContainerStyle={styles.options}
        showsVerticalScrollIndicator={false}
      >
        {allocationResponse.options.map((option, index) => (
          <AllocationCard
            key={option.option_id}
            option={option}
            selected={selectedAllocationIndex === index}
            recommended={allocationResponse.recommended_option === index}
            onPress={() => selectAllocation(index)}
          />
        ))}
      </ScrollView>

      {/* Bottom CTA */}
      <View style={[styles.bottom, { paddingBottom: insets.bottom + Spacing.md }]}>
        <GradientButton
          title={isGenerating ? 'Generating...' : 'Generate Itinerary'}
          onPress={handleGenerate}
          disabled={selectedAllocationIndex == null || isGenerating}
        />
      </View>
    </View>
  );
}

function AllocationCard({
  option, selected, recommended, onPress,
}: {
  option: CityAllocationOption;
  selected: boolean;
  recommended: boolean;
  onPress: () => void;
}) {
  return (
    <Pressable
      style={[styles.card, selected && styles.cardSelected]}
      onPress={onPress}
    >
      {recommended && (
        <LinearGradient
          colors={[Colors.primary, Colors.primaryLight]}
          start={{ x: 0, y: 0 }}
          end={{ x: 1, y: 0 }}
          style={styles.recommendedBadge}
        >
          <Ionicons name="star" size={12} color={Colors.white} />
          <Text style={styles.recommendedText}>Recommended</Text>
        </LinearGradient>
      )}

      <View style={styles.cardTop}>
        <MatchScoreCircle score={option.match_score} />
        <View style={{ flex: 1 }}>
          <Text style={Typography.titleSmall}>{option.option_name}</Text>
          <Text style={[Typography.bodySmall, { marginTop: 2 }]}>{option.description}</Text>
        </View>
      </View>

      {/* City breakdown */}
      <View style={styles.cityList}>
        {option.cities.map((city) => (
          <View key={city.city_id} style={styles.cityRow}>
            <Text style={Typography.labelMedium}>{city.city_name}</Text>
            <View style={styles.cityBar}>
              <View
                style={[
                  styles.cityBarFill,
                  { width: `${(city.days / option.total_days) * 100}%` },
                ]}
              />
            </View>
            <Text style={Typography.labelSmall}>{city.days}d</Text>
          </View>
        ))}
      </View>

      {/* Pros & Cons */}
      <View style={styles.prosConsRow}>
        <View style={{ flex: 1 }}>
          {option.pros.slice(0, 2).map((pro, i) => (
            <View key={i} style={styles.prosItem}>
              <Ionicons name="checkmark-circle" size={14} color={Colors.success} />
              <Text style={[Typography.caption, { color: Colors.textSecondary, flex: 1 }]}>{pro}</Text>
            </View>
          ))}
        </View>
        <View style={{ flex: 1 }}>
          {option.cons.slice(0, 2).map((con, i) => (
            <View key={i} style={styles.prosItem}>
              <Ionicons name="alert-circle" size={14} color={Colors.warning} />
              <Text style={[Typography.caption, { color: Colors.textSecondary, flex: 1 }]}>{con}</Text>
            </View>
          ))}
        </View>
      </View>
    </Pressable>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: Colors.background,
  },
  loadingContainer: {
    flex: 1,
    backgroundColor: Colors.background,
    alignItems: 'center',
    justifyContent: 'center',
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: Spacing.sm,
    paddingHorizontal: Spacing.md,
    paddingVertical: Spacing.md,
  },
  backBtn: {
    width: 40,
    height: 40,
    borderRadius: Radius.md,
    backgroundColor: Colors.surface,
    alignItems: 'center',
    justifyContent: 'center',
    borderWidth: 1,
    borderColor: Colors.border,
  },
  options: {
    paddingHorizontal: Spacing.md,
    gap: Spacing.md,
    paddingBottom: 120,
  },
  card: {
    backgroundColor: Colors.surface,
    borderRadius: Radius.xl,
    padding: Spacing.md,
    borderWidth: 2,
    borderColor: Colors.border,
    gap: Spacing.md,
  },
  cardSelected: {
    borderColor: Colors.primary,
  },
  recommendedBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 4,
    alignSelf: 'flex-start',
    paddingHorizontal: Spacing.sm,
    paddingVertical: 4,
    borderRadius: Radius.full,
  },
  recommendedText: {
    ...Typography.labelSmall,
    color: Colors.white,
    fontSize: 10,
  },
  cardTop: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: Spacing.md,
  },
  cityList: {
    gap: Spacing.xs,
  },
  cityRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: Spacing.xs,
  },
  cityBar: {
    flex: 1,
    height: 6,
    backgroundColor: Colors.surfaceVariant,
    borderRadius: 3,
    overflow: 'hidden',
  },
  cityBarFill: {
    height: '100%',
    backgroundColor: Colors.primary,
    borderRadius: 3,
  },
  prosConsRow: {
    flexDirection: 'row',
    gap: Spacing.sm,
  },
  prosItem: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    gap: 4,
    marginBottom: 2,
  },
  bottom: {
    position: 'absolute',
    bottom: 0,
    left: 0,
    right: 0,
    backgroundColor: Colors.surface,
    padding: Spacing.md,
    borderTopWidth: 1,
    borderTopColor: Colors.border,
  },
});
