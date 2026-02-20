import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  Pressable,
  TextInput,
  Platform,
} from 'react-native';
import { useRouter } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import { useCountryStore } from '@/stores/countryStore';
import { GradientButton } from '@/components/GradientButton';
import { StepIndicator } from '@/components/StepIndicator';
import { ChipSelector } from '@/components/ChipSelector';
import { Colors, Typography, Spacing, Radius, vibeColor, groupTypeColor } from '@/theme';

const GROUP_TYPES = [
  { id: 'solo', label: 'Solo', icon: 'person-outline' as const },
  { id: 'couple', label: 'Couple', icon: 'heart-outline' as const },
  { id: 'family', label: 'Family', icon: 'people-outline' as const },
  { id: 'friends', label: 'Friends', icon: 'happy-outline' as const },
];

const VIBES = [
  'cultural', 'foodie', 'romantic', 'adventure', 'relaxation',
  'nature', 'shopping', 'nightlife', 'historical', 'artsy',
];

const PACING_OPTIONS = [
  { id: 'slow', label: 'Slow', desc: 'Relaxed pace, fewer activities', icon: 'leaf-outline' as const },
  { id: 'moderate', label: 'Moderate', desc: 'Balanced mix', icon: 'walk-outline' as const },
  { id: 'fast', label: 'Fast', desc: 'Pack in as much as possible', icon: 'flash-outline' as const },
];

export default function TripPreferencesScreen() {
  const router = useRouter();
  const insets = useSafeAreaInsets();
  const store = useCountryStore();
  const {
    currentStep, selectedCountry,
    startDate, endDate,
    groupType, groupSize,
    vibes, budgetLevel, pacing,
    nextStep, previousStep,
    setDateRange, setGroupType, setGroupSize,
    toggleVibe, setBudgetLevel, setPacing,
    fetchAllocations,
  } = store;

  // Local date state for simple date input (no native picker for simplicity)
  const [localStart, setLocalStart] = useState(startDate ?? '');
  const [localEnd, setLocalEnd] = useState(endDate ?? '');

  const handleNext = async () => {
    if (currentStep === 0 && localStart && localEnd) {
      setDateRange(localStart, localEnd);
    }
    if (currentStep === 3) {
      // Final step — fetch allocations and navigate
      if (localStart && localEnd) setDateRange(localStart, localEnd);
      await fetchAllocations();
      router.push('/country/allocations');
    } else {
      nextStep();
    }
  };

  const handleBack = () => {
    if (currentStep === 0) {
      router.back();
    } else {
      previousStep();
    }
  };

  const canProceed = () => {
    switch (currentStep) {
      case 0: return localStart.length >= 10 && localEnd.length >= 10;
      case 1: return groupType !== '';
      case 2: return vibes.length > 0;
      case 3: return true;
      default: return false;
    }
  };

  return (
    <View style={[styles.container, { paddingTop: insets.top }]}>
      {/* Header */}
      <View style={styles.header}>
        <Pressable onPress={handleBack} style={styles.backBtn}>
          <Ionicons name="arrow-back" size={22} color={Colors.textPrimary} />
        </Pressable>
        <View style={{ flex: 1 }}>
          <Text style={Typography.titleLarge}>Trip Preferences</Text>
          <Text style={[Typography.bodySmall, { marginTop: 2 }]}>
            {selectedCountry?.name ?? 'Country'} trip
          </Text>
        </View>
      </View>

      <StepIndicator steps={4} current={currentStep} />

      <ScrollView
        contentContainerStyle={styles.stepContent}
        showsVerticalScrollIndicator={false}
      >
        {currentStep === 0 && (
          <DateStep
            startDate={localStart}
            endDate={localEnd}
            onStartChange={setLocalStart}
            onEndChange={setLocalEnd}
          />
        )}
        {currentStep === 1 && (
          <GroupStep
            groupType={groupType}
            groupSize={groupSize}
            onTypeChange={setGroupType}
            onSizeChange={setGroupSize}
          />
        )}
        {currentStep === 2 && (
          <VibeStep vibes={vibes} onToggle={toggleVibe} />
        )}
        {currentStep === 3 && (
          <PacingBudgetStep
            pacing={pacing}
            budgetLevel={budgetLevel}
            onPacingChange={setPacing}
            onBudgetChange={setBudgetLevel}
          />
        )}
      </ScrollView>

      {/* Bottom CTA */}
      <View style={[styles.bottom, { paddingBottom: insets.bottom + Spacing.md }]}>
        <GradientButton
          title={currentStep === 3 ? 'See Options' : 'Continue'}
          onPress={handleNext}
          disabled={!canProceed()}
        />
      </View>
    </View>
  );
}

// ============== Step Sub-components ==============

function DateStep({
  startDate, endDate, onStartChange, onEndChange,
}: {
  startDate: string; endDate: string;
  onStartChange: (v: string) => void; onEndChange: (v: string) => void;
}) {
  return (
    <View style={styles.stepContainer}>
      <Text style={Typography.titleMedium}>When are you traveling?</Text>
      <Text style={[Typography.bodySmall, { marginTop: 4, marginBottom: Spacing.lg }]}>
        Enter dates as YYYY-MM-DD
      </Text>

      <Text style={[Typography.labelLarge, { marginBottom: Spacing.xs }]}>Start Date</Text>
      <TextInput
        style={styles.dateInput}
        value={startDate}
        onChangeText={onStartChange}
        placeholder="2026-03-15"
        placeholderTextColor={Colors.textDisabled}
        keyboardType={Platform.OS === 'ios' ? 'numbers-and-punctuation' : 'default'}
      />

      <Text style={[Typography.labelLarge, { marginBottom: Spacing.xs, marginTop: Spacing.md }]}>End Date</Text>
      <TextInput
        style={styles.dateInput}
        value={endDate}
        onChangeText={onEndChange}
        placeholder="2026-03-25"
        placeholderTextColor={Colors.textDisabled}
        keyboardType={Platform.OS === 'ios' ? 'numbers-and-punctuation' : 'default'}
      />

      {startDate.length >= 10 && endDate.length >= 10 && (
        <View style={styles.dateSummary}>
          <Ionicons name="calendar-outline" size={18} color={Colors.primary} />
          <Text style={[Typography.labelLarge, { color: Colors.primary }]}>
            {Math.round((new Date(endDate).getTime() - new Date(startDate).getTime()) / 86400000) + 1} days
          </Text>
        </View>
      )}
    </View>
  );
}

function GroupStep({
  groupType, groupSize, onTypeChange, onSizeChange,
}: {
  groupType: string; groupSize: number;
  onTypeChange: (v: string) => void; onSizeChange: (v: number) => void;
}) {
  return (
    <View style={styles.stepContainer}>
      <Text style={Typography.titleMedium}>Who's traveling?</Text>
      <Text style={[Typography.bodySmall, { marginTop: 4, marginBottom: Spacing.lg }]}>
        Choose your group type
      </Text>

      <View style={styles.groupGrid}>
        {GROUP_TYPES.map((g) => {
          const selected = groupType === g.id;
          const color = groupTypeColor(g.id);
          return (
            <Pressable
              key={g.id}
              style={[styles.groupCard, selected && { borderColor: color, backgroundColor: color + '10' }]}
              onPress={() => onTypeChange(g.id)}
            >
              <Ionicons name={g.icon} size={28} color={selected ? color : Colors.textTertiary} />
              <Text style={[Typography.labelLarge, selected && { color }]}>{g.label}</Text>
            </Pressable>
          );
        })}
      </View>

      {/* Size stepper */}
      <View style={styles.stepper}>
        <Text style={Typography.labelLarge}>Group Size</Text>
        <View style={styles.stepperControls}>
          <Pressable
            style={styles.stepperBtn}
            onPress={() => onSizeChange(groupSize - 1)}
          >
            <Ionicons name="remove" size={18} color={Colors.textPrimary} />
          </Pressable>
          <Text style={[Typography.titleMedium, { minWidth: 32, textAlign: 'center' }]}>
            {groupSize}
          </Text>
          <Pressable
            style={styles.stepperBtn}
            onPress={() => onSizeChange(groupSize + 1)}
          >
            <Ionicons name="add" size={18} color={Colors.textPrimary} />
          </Pressable>
        </View>
      </View>
    </View>
  );
}

function VibeStep({
  vibes, onToggle,
}: {
  vibes: string[]; onToggle: (v: string) => void;
}) {
  return (
    <View style={styles.stepContainer}>
      <Text style={Typography.titleMedium}>What vibes are you after?</Text>
      <Text style={[Typography.bodySmall, { marginTop: 4, marginBottom: Spacing.lg }]}>
        Select up to 5 travel vibes
      </Text>
      <ChipSelector
        options={VIBES}
        selected={vibes}
        onToggle={onToggle}
        max={5}
        colorMap={vibeColor}
      />
      <Text style={[Typography.caption, { marginTop: Spacing.sm }]}>
        {vibes.length}/5 selected
      </Text>
    </View>
  );
}

function PacingBudgetStep({
  pacing, budgetLevel, onPacingChange, onBudgetChange,
}: {
  pacing: string; budgetLevel: number;
  onPacingChange: (v: string) => void; onBudgetChange: (v: number) => void;
}) {
  return (
    <View style={styles.stepContainer}>
      <Text style={Typography.titleMedium}>Pace & Budget</Text>
      <Text style={[Typography.bodySmall, { marginTop: 4, marginBottom: Spacing.lg }]}>
        How do you like to travel?
      </Text>

      {/* Pacing */}
      <View style={{ gap: Spacing.sm, marginBottom: Spacing.xl }}>
        {PACING_OPTIONS.map((p) => {
          const selected = pacing === p.id;
          return (
            <Pressable
              key={p.id}
              style={[styles.pacingCard, selected && styles.pacingCardSelected]}
              onPress={() => onPacingChange(p.id)}
            >
              <Ionicons
                name={p.icon}
                size={24}
                color={selected ? Colors.primary : Colors.textTertiary}
              />
              <View style={{ flex: 1 }}>
                <Text style={[Typography.labelLarge, selected && { color: Colors.primary }]}>
                  {p.label}
                </Text>
                <Text style={Typography.caption}>{p.desc}</Text>
              </View>
              {selected && (
                <Ionicons name="checkmark-circle" size={22} color={Colors.primary} />
              )}
            </Pressable>
          );
        })}
      </View>

      {/* Budget */}
      <Text style={[Typography.labelLarge, { marginBottom: Spacing.sm }]}>Budget Level</Text>
      <View style={styles.budgetRow}>
        {[1, 2, 3, 4, 5].map((level) => (
          <Pressable
            key={level}
            style={[
              styles.budgetDot,
              level <= budgetLevel && styles.budgetDotActive,
            ]}
            onPress={() => onBudgetChange(level)}
          >
            <Text style={[
              Typography.labelMedium,
              { color: level <= budgetLevel ? Colors.primary : Colors.textDisabled },
            ]}>
              $
            </Text>
          </Pressable>
        ))}
      </View>
      <Text style={[Typography.caption, { marginTop: Spacing.xs }]}>
        {['', 'Budget', 'Economy', 'Mid-range', 'Premium', 'Luxury'][budgetLevel]}
      </Text>
    </View>
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
  stepContent: {
    paddingBottom: 120,
  },
  stepContainer: {
    paddingHorizontal: Spacing.lg,
  },
  dateInput: {
    backgroundColor: Colors.surface,
    borderRadius: Radius.md,
    borderWidth: 1,
    borderColor: Colors.border,
    paddingHorizontal: Spacing.md,
    paddingVertical: Spacing.sm,
    ...Typography.bodyLarge,
    color: Colors.textPrimary,
  },
  dateSummary: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: Spacing.xs,
    marginTop: Spacing.md,
    paddingVertical: Spacing.sm,
    paddingHorizontal: Spacing.md,
    backgroundColor: Colors.secondary,
    borderRadius: Radius.md,
    alignSelf: 'flex-start',
  },
  groupGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: Spacing.sm,
  },
  groupCard: {
    width: '47%',
    backgroundColor: Colors.surface,
    borderRadius: Radius.lg,
    padding: Spacing.md,
    alignItems: 'center',
    gap: Spacing.xs,
    borderWidth: 2,
    borderColor: Colors.border,
  },
  stepper: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginTop: Spacing.xl,
    backgroundColor: Colors.surface,
    borderRadius: Radius.md,
    padding: Spacing.md,
    borderWidth: 1,
    borderColor: Colors.border,
  },
  stepperControls: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: Spacing.sm,
  },
  stepperBtn: {
    width: 36,
    height: 36,
    borderRadius: 18,
    backgroundColor: Colors.surfaceVariant,
    alignItems: 'center',
    justifyContent: 'center',
  },
  pacingCard: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: Spacing.sm,
    backgroundColor: Colors.surface,
    borderRadius: Radius.lg,
    padding: Spacing.md,
    borderWidth: 2,
    borderColor: Colors.border,
  },
  pacingCardSelected: {
    borderColor: Colors.primary,
    backgroundColor: Colors.secondary,
  },
  budgetRow: {
    flexDirection: 'row',
    gap: Spacing.sm,
  },
  budgetDot: {
    width: 44,
    height: 44,
    borderRadius: 22,
    backgroundColor: Colors.surface,
    alignItems: 'center',
    justifyContent: 'center',
    borderWidth: 2,
    borderColor: Colors.border,
  },
  budgetDotActive: {
    borderColor: Colors.primary,
    backgroundColor: Colors.secondary,
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
