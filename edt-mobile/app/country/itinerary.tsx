import React, { useState, useMemo } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  Pressable,
  Dimensions,
} from 'react-native';
import { useRouter } from 'expo-router';
import { LinearGradient } from 'expo-linear-gradient';
import { Ionicons } from '@expo/vector-icons';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import { useCountryStore } from '@/stores/countryStore';
import { GlassContainer } from '@/components/GlassContainer';
import { ActivityCard } from '@/components/ActivityCard';
import { TimelineMarker } from '@/components/TimelineMarker';
import { TransitConnector } from '@/components/TransitConnector';
import { Colors, Typography, Spacing, Radius, activityTypeColors } from '@/theme';
import type { DayItinerary, ActivityEntry } from '@/types';

const { width } = Dimensions.get('window');

export default function CountryItineraryScreen() {
  const router = useRouter();
  const insets = useSafeAreaInsets();
  const { countryItinerary, dayItineraries, selectedCountry } = useCountryStore();
  const [activeDayIndex, setActiveDayIndex] = useState(0);

  const activeDay = dayItineraries[activeDayIndex];
  const countryName = countryItinerary?.country_name ?? selectedCountry?.name ?? 'Trip';

  // Format date tabs
  const dateTabs = useMemo(
    () =>
      dayItineraries.map((d) => {
        const date = new Date(d.date);
        const day = date.toLocaleDateString('en-US', { day: 'numeric' });
        const month = date.toLocaleDateString('en-US', { month: 'short' });
        return `${day} ${month}`;
      }),
    [dayItineraries],
  );

  if (!activeDay) {
    return (
      <View style={[styles.emptyContainer, { paddingTop: insets.top }]}>
        <Ionicons name="document-text-outline" size={48} color={Colors.textTertiary} />
        <Text style={[Typography.titleSmall, { marginTop: Spacing.md }]}>
          No itinerary generated yet
        </Text>
        <Pressable onPress={() => router.back()} style={{ marginTop: Spacing.md }}>
          <Text style={[Typography.button, { color: Colors.primary }]}>Go Back</Text>
        </Pressable>
      </View>
    );
  }

  return (
    <View style={[styles.container, { paddingTop: insets.top }]}>
      {/* Glass Header */}
      <GlassContainer style={styles.glassHeader}>
        <View style={styles.headerRow}>
          <Pressable onPress={() => router.back()} style={styles.backBtn}>
            <Ionicons name="arrow-back" size={20} color={Colors.textPrimary} />
          </Pressable>
          <View style={styles.headerCenter}>
            <Text style={styles.headerSubtitle}>
              Day {activeDay.dayNumber} in {activeDay.cityName}
            </Text>
            <Text style={Typography.titleLarge}>{countryName}</Text>
          </View>
          <View style={{ width: 40 }} />
        </View>
      </GlassContainer>

      {/* Date Tabs */}
      <GlassContainer style={styles.dateTabsContainer}>
        <ScrollView
          horizontal
          showsHorizontalScrollIndicator={false}
          contentContainerStyle={styles.dateTabs}
        >
          {dateTabs.map((label, index) => {
            const isActive = index === activeDayIndex;
            return (
              <Pressable
                key={index}
                onPress={() => setActiveDayIndex(index)}
                style={styles.dateTabBtn}
              >
                {isActive ? (
                  <LinearGradient
                    colors={[Colors.primary, Colors.primaryLight]}
                    start={{ x: 0, y: 0 }}
                    end={{ x: 1, y: 1 }}
                    style={styles.dateTabActive}
                  >
                    <Text style={styles.dateTabTextActive}>{label}</Text>
                  </LinearGradient>
                ) : (
                  <Text style={styles.dateTabText}>{label}</Text>
                )}
              </Pressable>
            );
          })}
        </ScrollView>
      </GlassContainer>

      {/* Day Content */}
      <ScrollView
        showsVerticalScrollIndicator={false}
        contentContainerStyle={styles.dayScroll}
      >
        {/* Day Hero Card */}
        <View style={styles.dayCard}>
          <DayHero day={activeDay} />
          <DaySummary day={activeDay} />

          {/* Timeline */}
          <View style={styles.timeline}>
            {/* Left time rail bg */}
            <View style={styles.timeRail} />

            {activeDay.activities.map((entry, index) => (
              <View key={entry.id}>
                {/* Transit connector */}
                {entry.transit && index > 0 && (
                  <TransitConnector transit={entry.transit} />
                )}

                {/* Activity item */}
                <View style={styles.activityRow}>
                  <TimelineMarker
                    time={entry.data.time}
                    status={entry.status}
                    isFirst={index === 0}
                    isLast={index === activeDay.activities.length - 1}
                  />
                  <View style={styles.activityContent}>
                    <ActivityCard data={entry.data} />
                  </View>
                </View>
              </View>
            ))}
          </View>
        </View>

        {/* Inter-city travel card (if next day is different city) */}
        {activeDayIndex < dayItineraries.length - 1 &&
          dayItineraries[activeDayIndex + 1].cityName !== activeDay.cityName && (
            <InterCityCard
              fromCity={activeDay.cityName}
              toCity={dayItineraries[activeDayIndex + 1].cityName}
            />
          )}
      </ScrollView>
    </View>
  );
}

// ============== Sub-components ==============

function DayHero({ day }: { day: DayItinerary }) {
  const fullDate = new Date(day.date).toLocaleDateString('en-US', {
    weekday: 'long',
    month: 'long',
    day: 'numeric',
    year: 'numeric',
  });

  return (
    <LinearGradient
      colors={[Colors.primary, Colors.primaryLight, '#818CF8']}
      start={{ x: 0, y: 0 }}
      end={{ x: 1, y: 1 }}
      style={styles.heroGradient}
    >
      <View style={styles.heroBadges}>
        <View style={styles.heroBadge}>
          <Text style={styles.heroBadgeText}>Day {String(day.dayNumber).padStart(2, '0')}</Text>
        </View>
        <View style={[styles.heroBadge, styles.heroBadgeGlass]}>
          <Text style={styles.heroBadgeText}>{fullDate}</Text>
        </View>
      </View>
      <Text style={styles.heroTitle}>{day.title}</Text>
      <View style={styles.heroLocation}>
        <Ionicons name="location-outline" size={14} color="rgba(255,255,255,0.8)" />
        <Text style={styles.heroLocationText}>{day.cityName}</Text>
      </View>
    </LinearGradient>
  );
}

function DaySummary({ day }: { day: DayItinerary }) {
  const activities = day.activities;
  const typeCounts: Record<string, number> = {};
  for (const a of activities) {
    typeCounts[a.data.type] = (typeCounts[a.data.type] ?? 0) + 1;
  }

  // Compute duration from first to last activity
  const times = activities
    .map((a) => a.data.time)
    .filter(Boolean)
    .sort();
  let duration = '';
  if (times.length >= 2) {
    const [h1, m1] = times[0].split(':').map(Number);
    const [h2, m2] = times[times.length - 1].split(':').map(Number);
    const totalMin = (h2 * 60 + m2) - (h1 * 60 + m1);
    const hours = Math.floor(totalMin / 60);
    const mins = totalMin % 60;
    duration = `${hours}h ${mins}m`;
  }

  const TYPE_ICONS: Record<string, keyof typeof Ionicons.glyphMap> = {
    hotel: 'bed-outline',
    meal: 'restaurant-outline',
    transport: 'train-outline',
    sightseeing: 'camera-outline',
    shopping: 'bag-outline',
  };

  return (
    <View style={styles.summaryContainer}>
      <View style={styles.summaryRow}>
        {duration ? (
          <>
            <Ionicons name="time-outline" size={14} color={Colors.textSecondary} />
            <Text style={Typography.caption}>{duration}</Text>
            <View style={styles.summaryDivider} />
          </>
        ) : null}
        <Ionicons name="location-outline" size={14} color={Colors.textSecondary} />
        <Text style={Typography.caption}>{activities.length} stops</Text>
        <View style={styles.summaryDivider} />
        {Object.entries(typeCounts).map(([type, count]) => {
          const colors = activityTypeColors(type);
          const icon = TYPE_ICONS[type];
          return (
            <View key={type} style={[styles.typeChip, { backgroundColor: colors.bg, borderColor: colors.border }]}>
              {icon && <Ionicons name={icon} size={12} color={colors.fg} />}
              <Text style={[styles.typeChipText, { color: colors.fg }]}>{count}</Text>
            </View>
          );
        })}
      </View>
    </View>
  );
}

function InterCityCard({ fromCity, toCity }: { fromCity: string; toCity: string }) {
  return (
    <View style={styles.interCityCard}>
      <LinearGradient
        colors={[Colors.activityTransportBg, Colors.surface]}
        style={styles.interCityGradient}
      >
        <Ionicons name="train-outline" size={24} color={Colors.activityTransport} />
        <View style={{ flex: 1 }}>
          <Text style={Typography.labelLarge}>Travel to next city</Text>
          <Text style={Typography.caption}>{fromCity} \u2192 {toCity}</Text>
        </View>
        <Ionicons name="chevron-forward" size={18} color={Colors.textTertiary} />
      </LinearGradient>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: Colors.background,
  },
  emptyContainer: {
    flex: 1,
    backgroundColor: Colors.background,
    alignItems: 'center',
    justifyContent: 'center',
  },

  // Glass Header
  glassHeader: {
    marginHorizontal: Spacing.sm,
    marginTop: Spacing.xs,
    paddingVertical: Spacing.sm,
    paddingHorizontal: Spacing.sm,
  },
  headerRow: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  backBtn: {
    width: 40,
    height: 40,
    borderRadius: Radius.lg,
    backgroundColor: 'rgba(255,255,255,0.6)',
    alignItems: 'center',
    justifyContent: 'center',
  },
  headerCenter: {
    flex: 1,
    alignItems: 'center',
  },
  headerSubtitle: {
    ...Typography.labelSmall,
    color: Colors.primary,
    textTransform: 'uppercase',
    letterSpacing: 2,
    fontSize: 10,
  },

  // Date Tabs
  dateTabsContainer: {
    marginHorizontal: Spacing.sm,
    marginTop: Spacing.xs,
    padding: 6,
  },
  dateTabs: {
    gap: 6,
  },
  dateTabBtn: {
    paddingHorizontal: 2,
  },
  dateTabActive: {
    paddingHorizontal: Spacing.md,
    paddingVertical: Spacing.xs,
    borderRadius: Radius.lg,
    shadowColor: Colors.primary,
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.25,
    shadowRadius: 6,
    elevation: 3,
  },
  dateTabTextActive: {
    ...Typography.labelMedium,
    color: Colors.white,
    fontFamily: 'PlusJakartaSans_600SemiBold',
  },
  dateTabText: {
    ...Typography.labelMedium,
    color: Colors.textTertiary,
    paddingHorizontal: Spacing.sm,
    paddingVertical: Spacing.xs,
  },

  // Day Content
  dayScroll: {
    paddingHorizontal: Spacing.sm,
    paddingTop: Spacing.sm,
    paddingBottom: Spacing.xxl + 40,
  },
  dayCard: {
    backgroundColor: Colors.surface,
    borderRadius: Radius.xxl,
    padding: Spacing.sm,
    shadowColor: Colors.shadowMedium,
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 1,
    shadowRadius: 12,
    elevation: 4,
    borderWidth: 1,
    borderColor: Colors.border + '50',
  },

  // Day Hero
  heroGradient: {
    borderRadius: Radius.xl,
    padding: Spacing.md,
    height: 144,
    justifyContent: 'flex-end',
    marginBottom: Spacing.sm,
  },
  heroBadges: {
    flexDirection: 'row',
    gap: Spacing.xs,
    marginBottom: Spacing.xs,
  },
  heroBadge: {
    paddingHorizontal: Spacing.xs,
    paddingVertical: 2,
    borderRadius: Radius.full,
    backgroundColor: 'rgba(255,255,255,0.2)',
  },
  heroBadgeGlass: {
    backgroundColor: 'rgba(255,255,255,0.15)',
  },
  heroBadgeText: {
    ...Typography.labelSmall,
    color: Colors.white,
    fontSize: 10,
    fontFamily: 'PlusJakartaSans_700Bold',
  },
  heroTitle: {
    ...Typography.titleMedium,
    color: Colors.white,
    fontFamily: 'PlusJakartaSans_800ExtraBold',
  },
  heroLocation: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 4,
    marginTop: 4,
  },
  heroLocationText: {
    ...Typography.caption,
    color: 'rgba(255,255,255,0.8)',
  },

  // Day Summary
  summaryContainer: {
    backgroundColor: Colors.secondary + '99',
    borderRadius: Radius.md,
    borderWidth: 1,
    borderColor: Colors.border + '50',
    marginBottom: Spacing.md,
    overflow: 'hidden',
  },
  summaryRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: Spacing.xs,
    paddingHorizontal: Spacing.sm,
    paddingVertical: Spacing.xs + 2,
    flexWrap: 'wrap',
  },
  summaryDivider: {
    width: 1,
    height: 14,
    backgroundColor: Colors.border,
    marginHorizontal: 2,
  },
  typeChip: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 3,
    paddingHorizontal: 8,
    paddingVertical: 2,
    borderRadius: Radius.full,
    borderWidth: 1,
  },
  typeChipText: {
    fontSize: 10,
    fontFamily: 'PlusJakartaSans_600SemiBold',
  },

  // Timeline
  timeline: {
    position: 'relative',
  },
  timeRail: {
    position: 'absolute',
    left: 0,
    top: 0,
    bottom: 0,
    width: 28,
    backgroundColor: Colors.surfaceVariant + '50',
    borderTopLeftRadius: Radius.sm,
    borderBottomLeftRadius: Radius.sm,
    borderRightWidth: 1,
    borderRightColor: Colors.border + '33',
  },
  activityRow: {
    position: 'relative',
    paddingLeft: 48,
    paddingVertical: 6,
    minHeight: 56,
  },
  activityContent: {
    flex: 1,
  },

  // Inter-city
  interCityCard: {
    marginTop: Spacing.md,
    borderRadius: Radius.xl,
    overflow: 'hidden',
    borderWidth: 1,
    borderColor: Colors.activityTransportBorder,
  },
  interCityGradient: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: Spacing.sm,
    padding: Spacing.md,
  },
});
