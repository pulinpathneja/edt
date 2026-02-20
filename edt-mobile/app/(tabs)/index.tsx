import React, { useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  Pressable,
  Dimensions,
} from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { useRouter } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import { useCountryStore } from '@/stores/countryStore';
import { Colors, Typography, Spacing, Radius } from '@/theme';

const { width } = Dimensions.get('window');
const CARD_WIDTH = 150;

const COUNTRY_GRADIENTS: Record<string, [string, string]> = {
  italy: ['#FF6B6B', '#EE5A24'],
  france: ['#4F6EF5', '#6C5CE7'],
  spain: ['#FDCB6E', '#F0932B'],
  japan: ['#FDA7DF', '#D980FA'],
  united_kingdom: ['#3B82F6', '#1E3A8A'],
};

export default function HomeScreen() {
  const router = useRouter();
  const insets = useSafeAreaInsets();
  const { countries, isLoadingCountries, loadCountries, selectCountry } = useCountryStore();

  useEffect(() => {
    if (countries.length === 0) loadCountries();
  }, []);

  return (
    <View style={[styles.container, { paddingTop: insets.top }]}>
      <ScrollView showsVerticalScrollIndicator={false} contentContainerStyle={styles.scroll}>
        {/* Header */}
        <LinearGradient
          colors={[Colors.surfaceWarm, Colors.background]}
          style={styles.header}
        >
          <Text style={Typography.headlineLarge}>Where to next?</Text>
          <Text style={[Typography.bodyMedium, { color: Colors.textSecondary, marginTop: 4 }]}>
            Plan your perfect multi-city adventure
          </Text>
        </LinearGradient>

        {/* Multi-City CTA */}
        <Pressable
          style={styles.ctaCard}
          onPress={() => router.push('/country/select')}
        >
          <LinearGradient
            colors={[Colors.primary, Colors.primaryLight]}
            start={{ x: 0, y: 0 }}
            end={{ x: 1, y: 1 }}
            style={styles.ctaGradient}
          >
            <Ionicons name="airplane-outline" size={28} color={Colors.white} />
            <View style={{ flex: 1 }}>
              <Text style={[Typography.titleSmall, { color: Colors.white }]}>
                Multi-City Country Trip
              </Text>
              <Text style={[Typography.bodySmall, { color: 'rgba(255,255,255,0.8)' }]}>
                Visit multiple cities in one trip
              </Text>
            </View>
            <Ionicons name="chevron-forward" size={20} color={Colors.white} />
          </LinearGradient>
        </Pressable>

        {/* Country Carousel */}
        <View style={styles.section}>
          <Text style={[Typography.titleMedium, styles.sectionTitle]}>
            Popular Destinations
          </Text>
          <ScrollView
            horizontal
            showsHorizontalScrollIndicator={false}
            contentContainerStyle={styles.carousel}
          >
            {countries.map((country) => {
              const gradient = COUNTRY_GRADIENTS[country.id] ?? [Colors.primary, Colors.primaryLight];
              return (
                <Pressable
                  key={country.id}
                  style={styles.countryCard}
                  onPress={() => {
                    selectCountry(country);
                    router.push('/country/select');
                  }}
                >
                  <LinearGradient
                    colors={gradient}
                    start={{ x: 0, y: 0 }}
                    end={{ x: 1, y: 1 }}
                    style={styles.countryCardGradient}
                  >
                    <Text style={styles.countryFlag}>{country.flag}</Text>
                    <Text style={styles.countryName}>{country.name}</Text>
                    <Text style={styles.countryCities}>
                      {country.cities.length} cities
                    </Text>
                  </LinearGradient>
                </Pressable>
              );
            })}
          </ScrollView>
        </View>

        {/* Quick Actions */}
        <View style={styles.section}>
          <Text style={[Typography.titleMedium, styles.sectionTitle]}>
            Quick Start
          </Text>
          <View style={styles.quickActions}>
            {[
              { icon: 'flame-outline' as const, label: 'Popular', desc: 'Trending routes' },
              { icon: 'heart-outline' as const, label: 'Romantic', desc: 'Couple getaways' },
              { icon: 'people-outline' as const, label: 'Family', desc: 'Kid-friendly trips' },
            ].map((action) => (
              <Pressable key={action.label} style={styles.quickCard}>
                <View style={styles.quickIcon}>
                  <Ionicons name={action.icon} size={22} color={Colors.primary} />
                </View>
                <Text style={Typography.labelLarge}>{action.label}</Text>
                <Text style={Typography.caption}>{action.desc}</Text>
              </Pressable>
            ))}
          </View>
        </View>
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: Colors.background,
  },
  scroll: {
    paddingBottom: Spacing.xxl,
  },
  header: {
    paddingHorizontal: Spacing.lg,
    paddingTop: Spacing.lg,
    paddingBottom: Spacing.xl,
  },
  ctaCard: {
    marginHorizontal: Spacing.md,
    borderRadius: Radius.xl,
    shadowColor: Colors.primary,
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.2,
    shadowRadius: 12,
    elevation: 6,
    marginBottom: Spacing.lg,
  },
  ctaGradient: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: Spacing.sm,
    paddingVertical: Spacing.md,
    paddingHorizontal: Spacing.lg,
    borderRadius: Radius.xl,
  },
  section: {
    marginBottom: Spacing.lg,
  },
  sectionTitle: {
    paddingHorizontal: Spacing.lg,
    marginBottom: Spacing.sm,
  },
  carousel: {
    paddingHorizontal: Spacing.md,
    gap: Spacing.sm,
  },
  countryCard: {
    width: CARD_WIDTH,
    height: 180,
    borderRadius: Radius.xl,
    overflow: 'hidden',
    shadowColor: Colors.shadowDark,
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.3,
    shadowRadius: 8,
    elevation: 4,
  },
  countryCardGradient: {
    flex: 1,
    padding: Spacing.md,
    justifyContent: 'flex-end',
  },
  countryFlag: {
    fontSize: 36,
    marginBottom: Spacing.xs,
  },
  countryName: {
    ...Typography.titleSmall,
    color: Colors.white,
  },
  countryCities: {
    ...Typography.caption,
    color: 'rgba(255,255,255,0.8)',
  },
  quickActions: {
    flexDirection: 'row',
    paddingHorizontal: Spacing.md,
    gap: Spacing.sm,
  },
  quickCard: {
    flex: 1,
    backgroundColor: Colors.surface,
    borderRadius: Radius.lg,
    padding: Spacing.md,
    borderWidth: 1,
    borderColor: Colors.border,
    gap: 4,
  },
  quickIcon: {
    width: 40,
    height: 40,
    borderRadius: Radius.md,
    backgroundColor: Colors.secondary,
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: 4,
  },
});
