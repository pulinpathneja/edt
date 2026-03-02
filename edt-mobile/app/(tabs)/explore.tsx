import React from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  Pressable,
  Image,
  Dimensions,
} from 'react-native';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import { Ionicons } from '@expo/vector-icons';
import { LinearGradient } from 'expo-linear-gradient';
import { Colors, Typography, Spacing, Radius, vibeColor } from '@/theme';

const { width } = Dimensions.get('window');
const CARD_WIDTH = width * 0.6;

// ── Static data ──────────────────────────────────────────────────

const TRENDING_CITIES = [
  {
    city: 'Rome',
    country: 'Italy',
    image: 'https://plus.unsplash.com/premium_photo-1661938399624-3495425e5027?w=800&h=500&fit=crop&auto=format',
    vibes: ['Cultural', 'Foodie', 'Historical'],
  },
  {
    city: 'Paris',
    country: 'France',
    image: 'https://plus.unsplash.com/premium_photo-1661919210043-fd847a58522d?w=800&h=500&fit=crop&auto=format',
    vibes: ['Romantic', 'Cultural', 'Artsy'],
  },
  {
    city: 'Tokyo',
    country: 'Japan',
    image: 'https://plus.unsplash.com/premium_photo-1697730244459-aafec2c71f64?w=800&h=500&fit=crop&auto=format',
    vibes: ['Cultural', 'Foodie', 'Adventure'],
  },
  {
    city: 'Barcelona',
    country: 'Spain',
    image: 'https://plus.unsplash.com/premium_photo-1661885514351-ad93dcfb25f3?w=800&h=500&fit=crop&auto=format',
    vibes: ['Cultural', 'Foodie', 'Nightlife'],
  },
  {
    city: 'Kyoto',
    country: 'Japan',
    image: 'https://images.unsplash.com/photo-1693378173709-2197ce8c5af3?w=800&h=500&fit=crop&auto=format',
    vibes: ['Cultural', 'Nature', 'Historical'],
  },
  {
    city: 'London',
    country: 'United Kingdom',
    image: 'https://plus.unsplash.com/premium_photo-1680806491784-6d3d0d406562?w=800&h=500&fit=crop&auto=format',
    vibes: ['Cultural', 'Historical', 'Shopping'],
  },
];

const VIBE_CARDS: { vibe: string; icon: keyof typeof Ionicons.glyphMap }[] = [
  { vibe: 'Cultural', icon: 'library-outline' },
  { vibe: 'Foodie', icon: 'restaurant-outline' },
  { vibe: 'Romantic', icon: 'heart-outline' },
  { vibe: 'Adventure', icon: 'compass-outline' },
  { vibe: 'Nature', icon: 'leaf-outline' },
  { vibe: 'Nightlife', icon: 'moon-outline' },
];

const POPULAR_ROUTES = [
  {
    title: 'Classic Italy',
    route: 'Rome \u2192 Florence \u2192 Venice',
    days: '10 days',
    vibes: ['Cultural', 'Foodie'],
  },
  {
    title: 'Japan Highlights',
    route: 'Tokyo \u2192 Kyoto \u2192 Osaka',
    days: '12 days',
    vibes: ['Cultural', 'Adventure'],
  },
  {
    title: 'Spain Explorer',
    route: 'Barcelona \u2192 Madrid \u2192 Seville',
    days: '11 days',
    vibes: ['Cultural', 'Nightlife'],
  },
];

// ── Component ────────────────────────────────────────────────────

export default function ExploreScreen() {
  const insets = useSafeAreaInsets();

  return (
    <ScrollView
      style={[styles.container, { paddingTop: insets.top }]}
      showsVerticalScrollIndicator={false}
    >
      {/* Header */}
      <View style={styles.header}>
        <Ionicons name="compass" size={24} color={Colors.primary} />
        <Text style={Typography.titleLarge}>Explore</Text>
      </View>

      {/* Trending Destinations */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Trending Destinations</Text>
        <ScrollView
          horizontal
          showsHorizontalScrollIndicator={false}
          contentContainerStyle={styles.horizontalScroll}
        >
          {TRENDING_CITIES.map((city) => (
            <View key={city.city} style={styles.cityCard}>
              <Image source={{ uri: city.image }} style={styles.cityImage} />
              <LinearGradient
                colors={['transparent', 'rgba(0,0,0,0.7)']}
                style={styles.cityOverlay}
              >
                <Text style={styles.cityName}>{city.city}</Text>
                <Text style={styles.cityCountry}>{city.country}</Text>
                <View style={styles.vibeRow}>
                  {city.vibes.map((v) => (
                    <View
                      key={v}
                      style={[styles.vibeChip, { backgroundColor: vibeColor(v) + '22', borderColor: vibeColor(v) + '55' }]}
                    >
                      <Text style={[styles.vibeChipText, { color: '#fff' }]}>{v}</Text>
                    </View>
                  ))}
                </View>
              </LinearGradient>
            </View>
          ))}
        </ScrollView>
      </View>

      {/* Travel by Vibe */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Travel by Vibe</Text>
        <View style={styles.vibeGrid}>
          {VIBE_CARDS.map((item) => {
            const color = vibeColor(item.vibe);
            return (
              <View key={item.vibe} style={[styles.vibeCard, { borderColor: color + '33' }]}>
                <View style={[styles.vibeIconCircle, { backgroundColor: color + '18' }]}>
                  <Ionicons name={item.icon} size={22} color={color} />
                </View>
                <Text style={[Typography.labelMedium, { color: Colors.textPrimary }]}>
                  {item.vibe}
                </Text>
              </View>
            );
          })}
        </View>
      </View>

      {/* Popular Routes */}
      <View style={[styles.section, { paddingBottom: insets.bottom + 80 }]}>
        <Text style={styles.sectionTitle}>Popular Routes</Text>
        {POPULAR_ROUTES.map((route) => (
          <View key={route.title} style={styles.routeCard}>
            <View style={styles.routeIcon}>
              <Ionicons name="map-outline" size={20} color={Colors.primary} />
            </View>
            <View style={styles.routeInfo}>
              <Text style={Typography.labelLarge}>{route.title}</Text>
              <Text style={[Typography.bodySmall, { color: Colors.textSecondary }]}>
                {route.route}
              </Text>
              <View style={styles.routeMeta}>
                <Ionicons name="time-outline" size={12} color={Colors.textTertiary} />
                <Text style={[Typography.caption, { color: Colors.textTertiary }]}>
                  {route.days}
                </Text>
                {route.vibes.map((v) => (
                  <View
                    key={v}
                    style={[styles.routeVibeChip, { backgroundColor: vibeColor(v) + '18' }]}
                  >
                    <Text style={[styles.routeVibeText, { color: vibeColor(v) }]}>{v}</Text>
                  </View>
                ))}
              </View>
            </View>
            <Ionicons name="chevron-forward" size={18} color={Colors.textTertiary} />
          </View>
        ))}
      </View>
    </ScrollView>
  );
}

// ── Styles ────────────────────────────────────────────────────────

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: Colors.background,
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: Spacing.sm,
    paddingHorizontal: Spacing.lg,
    paddingVertical: Spacing.md,
  },
  section: {
    marginTop: Spacing.md,
  },
  sectionTitle: {
    ...Typography.titleSmall,
    paddingHorizontal: Spacing.lg,
    marginBottom: Spacing.sm,
  },

  // Trending
  horizontalScroll: {
    paddingHorizontal: Spacing.lg,
    gap: Spacing.sm,
  },
  cityCard: {
    width: CARD_WIDTH,
    height: CARD_WIDTH * 0.75,
    borderRadius: Radius.xl,
    overflow: 'hidden',
  },
  cityImage: {
    ...StyleSheet.absoluteFillObject,
    width: '100%',
    height: '100%',
  },
  cityOverlay: {
    ...StyleSheet.absoluteFillObject,
    justifyContent: 'flex-end',
    padding: Spacing.sm,
  },
  cityName: {
    ...Typography.titleMedium,
    color: Colors.white,
    fontFamily: 'PlusJakartaSans_700Bold',
  },
  cityCountry: {
    ...Typography.caption,
    color: 'rgba(255,255,255,0.8)',
  },
  vibeRow: {
    flexDirection: 'row',
    gap: 4,
    marginTop: 4,
  },
  vibeChip: {
    paddingHorizontal: 6,
    paddingVertical: 2,
    borderRadius: Radius.full,
    borderWidth: 1,
  },
  vibeChipText: {
    fontSize: 10,
    fontFamily: 'PlusJakartaSans_600SemiBold',
  },

  // Vibe Grid
  vibeGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    paddingHorizontal: Spacing.lg,
    gap: Spacing.sm,
  },
  vibeCard: {
    width: (width - Spacing.lg * 2 - Spacing.sm * 2) / 3,
    alignItems: 'center',
    paddingVertical: Spacing.md,
    backgroundColor: Colors.surface,
    borderRadius: Radius.lg,
    borderWidth: 1,
    gap: Spacing.xs,
  },
  vibeIconCircle: {
    width: 44,
    height: 44,
    borderRadius: 22,
    alignItems: 'center',
    justifyContent: 'center',
  },

  // Routes
  routeCard: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: Spacing.sm,
    marginHorizontal: Spacing.lg,
    marginBottom: Spacing.sm,
    backgroundColor: Colors.surface,
    borderRadius: Radius.lg,
    padding: Spacing.sm,
    borderWidth: 1,
    borderColor: Colors.border,
  },
  routeIcon: {
    width: 40,
    height: 40,
    borderRadius: Radius.md,
    backgroundColor: Colors.secondary,
    alignItems: 'center',
    justifyContent: 'center',
  },
  routeInfo: {
    flex: 1,
    gap: 2,
  },
  routeMeta: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 4,
    marginTop: 2,
  },
  routeVibeChip: {
    paddingHorizontal: 6,
    paddingVertical: 1,
    borderRadius: Radius.full,
  },
  routeVibeText: {
    fontSize: 10,
    fontFamily: 'PlusJakartaSans_600SemiBold',
  },
});
