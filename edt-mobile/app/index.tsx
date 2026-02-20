import React from 'react';
import { View, Text, StyleSheet, Dimensions } from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { useRouter } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { GradientButton } from '@/components/GradientButton';
import { Colors, Typography, Spacing } from '@/theme';

const { height } = Dimensions.get('window');

export default function OnboardingScreen() {
  const router = useRouter();

  return (
    <LinearGradient
      colors={[Colors.primary, Colors.primaryLight, '#818CF8']}
      start={{ x: 0, y: 0 }}
      end={{ x: 1, y: 1 }}
      style={styles.container}
    >
      <View style={styles.content}>
        {/* Logo area */}
        <View style={styles.logoArea}>
          <View style={styles.logoCircle}>
            <Ionicons name="compass" size={48} color={Colors.primary} />
          </View>
          <Text style={styles.appName}>EDT</Text>
          <Text style={styles.tagline}>Explore. Discover. Travel.</Text>
        </View>

        {/* Description */}
        <View style={styles.descArea}>
          <Text style={styles.headline}>Plan your perfect multi-city adventure</Text>
          <Text style={styles.subtitle}>
            AI-powered itineraries tailored to your group, vibes, and pace
          </Text>
        </View>

        {/* CTA */}
        <View style={styles.ctaArea}>
          <GradientButton
            title="Get Started"
            onPress={() => router.replace('/(tabs)')}
            style={styles.ctaButton}
            textStyle={{ fontSize: 16 }}
          />
        </View>
      </View>
    </LinearGradient>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  content: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingHorizontal: Spacing.lg,
  },
  logoArea: {
    alignItems: 'center',
    marginBottom: height * 0.08,
  },
  logoCircle: {
    width: 88,
    height: 88,
    borderRadius: 44,
    backgroundColor: 'rgba(255,255,255,0.95)',
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: Spacing.md,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.15,
    shadowRadius: 12,
    elevation: 8,
  },
  appName: {
    ...Typography.displaySmall,
    color: Colors.white,
    letterSpacing: 6,
  },
  tagline: {
    ...Typography.bodyMedium,
    color: 'rgba(255,255,255,0.8)',
    marginTop: Spacing.xxs,
    letterSpacing: 1,
  },
  descArea: {
    alignItems: 'center',
    marginBottom: height * 0.08,
    paddingHorizontal: Spacing.lg,
  },
  headline: {
    ...Typography.headlineSmall,
    color: Colors.white,
    textAlign: 'center',
    marginBottom: Spacing.sm,
  },
  subtitle: {
    ...Typography.bodyMedium,
    color: 'rgba(255,255,255,0.75)',
    textAlign: 'center',
  },
  ctaArea: {
    width: '100%',
    paddingHorizontal: Spacing.lg,
  },
  ctaButton: {
    shadowColor: '#000',
    shadowOpacity: 0.3,
  },
});
