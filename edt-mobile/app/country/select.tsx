import React, { useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  Pressable,
} from 'react-native';
import { useRouter } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import { useCountryStore } from '@/stores/countryStore';
import { GradientButton } from '@/components/GradientButton';
import { Colors, Typography, Spacing, Radius } from '@/theme';
import type { CountryInfo } from '@/types';

export default function CountrySelectionScreen() {
  const router = useRouter();
  const insets = useSafeAreaInsets();
  const { countries, selectedCountry, loadCountries, selectCountry } = useCountryStore();

  useEffect(() => {
    if (countries.length === 0) loadCountries();
  }, []);

  return (
    <View style={[styles.container, { paddingTop: insets.top }]}>
      {/* Header */}
      <View style={styles.header}>
        <Pressable onPress={() => router.back()} style={styles.backBtn}>
          <Ionicons name="arrow-back" size={22} color={Colors.textPrimary} />
        </Pressable>
        <View>
          <Text style={Typography.titleLarge}>Choose a Country</Text>
          <Text style={[Typography.bodySmall, { marginTop: 2 }]}>
            Select your destination
          </Text>
        </View>
      </View>

      {/* Country Grid */}
      <ScrollView
        contentContainerStyle={styles.grid}
        showsVerticalScrollIndicator={false}
      >
        {countries.map((country) => (
          <CountryCard
            key={country.id}
            country={country}
            selected={selectedCountry?.id === country.id}
            onPress={() => selectCountry(country)}
          />
        ))}
      </ScrollView>

      {/* Bottom CTA */}
      <View style={[styles.bottom, { paddingBottom: insets.bottom + Spacing.md }]}>
        <GradientButton
          title="Continue"
          onPress={() => router.push('/country/preferences')}
          disabled={!selectedCountry}
        />
      </View>
    </View>
  );
}

function CountryCard({
  country,
  selected,
  onPress,
}: {
  country: CountryInfo;
  selected: boolean;
  onPress: () => void;
}) {
  const topCities = country.cities.slice(0, 3).map((c) => c.name);

  return (
    <Pressable
      onPress={onPress}
      style={[
        styles.card,
        selected && styles.cardSelected,
      ]}
    >
      <View style={styles.cardHeader}>
        <Text style={styles.flag}>{country.flag}</Text>
        {selected && (
          <View style={styles.checkBadge}>
            <Ionicons name="checkmark" size={14} color={Colors.white} />
          </View>
        )}
      </View>

      <Text style={[Typography.titleSmall, { marginTop: Spacing.xs }]}>
        {country.name}
      </Text>
      <Text style={[Typography.caption, { marginTop: 2 }]}>
        {country.cities.length} cities
      </Text>

      <View style={styles.cityChips}>
        {topCities.map((city) => (
          <View key={city} style={styles.cityChip}>
            <Text style={styles.cityChipText}>{city}</Text>
          </View>
        ))}
      </View>
    </Pressable>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: Colors.background,
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
  grid: {
    paddingHorizontal: Spacing.md,
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: Spacing.sm,
    paddingBottom: 120,
  },
  card: {
    width: '48%',
    backgroundColor: Colors.surface,
    borderRadius: Radius.xl,
    padding: Spacing.md,
    borderWidth: 2,
    borderColor: Colors.border,
  },
  cardSelected: {
    borderColor: Colors.primary,
    backgroundColor: Colors.secondary,
  },
  cardHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
  },
  flag: {
    fontSize: 32,
  },
  checkBadge: {
    width: 24,
    height: 24,
    borderRadius: 12,
    backgroundColor: Colors.primary,
    alignItems: 'center',
    justifyContent: 'center',
  },
  cityChips: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 4,
    marginTop: Spacing.xs,
  },
  cityChip: {
    backgroundColor: Colors.surfaceVariant,
    paddingHorizontal: 8,
    paddingVertical: 2,
    borderRadius: Radius.full,
  },
  cityChipText: {
    ...Typography.labelSmall,
    fontSize: 10,
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
