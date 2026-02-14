import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';
import 'package:go_router/go_router.dart';

import '../../../config/routes/app_router.dart';
import '../../../theme/colors/app_colors.dart';
import '../../../theme/spacing/app_spacing.dart';
import '../../widgets/atoms/app_button.dart';

/// Onboarding/welcome screen
class OnboardingScreen extends StatelessWidget {
  const OnboardingScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Container(
        decoration: const BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topCenter,
            end: Alignment.bottomCenter,
            colors: [
              AppColors.primary,
              AppColors.primaryDark,
            ],
          ),
        ),
        child: SafeArea(
          child: Padding(
            padding: const EdgeInsets.all(AppSpacing.lg),
            child: Column(
              children: [
                const Spacer(flex: 2),

                // Logo/Icon
                Container(
                  width: 120,
                  height: 120,
                  decoration: BoxDecoration(
                    color: AppColors.white.withOpacity(0.15),
                    shape: BoxShape.circle,
                  ),
                  child: const Center(
                    child: Text(
                      '✈️',
                      style: TextStyle(fontSize: 56),
                    ),
                  ),
                )
                    .animate()
                    .scale(
                      duration: const Duration(milliseconds: 600),
                      curve: Curves.elasticOut,
                    )
                    .fadeIn(),

                const SizedBox(height: AppSpacing.xl),

                // Title
                const Text(
                  'Travel Itinerary',
                  style: TextStyle(
                    fontSize: 32,
                    fontWeight: FontWeight.w700,
                    color: AppColors.white,
                  ),
                  textAlign: TextAlign.center,
                )
                    .animate(delay: const Duration(milliseconds: 200))
                    .fadeIn()
                    .slideY(begin: 0.3),

                const SizedBox(height: AppSpacing.md),

                // Subtitle
                Text(
                  'Your AI-powered travel companion.\nCreate personalized itineraries in minutes.',
                  style: TextStyle(
                    fontSize: 16,
                    color: AppColors.white.withOpacity(0.85),
                    height: 1.5,
                  ),
                  textAlign: TextAlign.center,
                )
                    .animate(delay: const Duration(milliseconds: 400))
                    .fadeIn()
                    .slideY(begin: 0.3),

                const Spacer(flex: 2),

                // Features list
                _FeatureItem(
                  icon: Icons.auto_awesome,
                  text: 'AI-curated experiences tailored to you',
                  delay: const Duration(milliseconds: 500),
                ),
                const SizedBox(height: AppSpacing.md),
                _FeatureItem(
                  icon: Icons.schedule,
                  text: 'Optimized daily schedules',
                  delay: const Duration(milliseconds: 600),
                ),
                const SizedBox(height: AppSpacing.md),
                _FeatureItem(
                  icon: Icons.restaurant,
                  text: 'Local dining recommendations',
                  delay: const Duration(milliseconds: 700),
                ),

                const Spacer(flex: 3),

                // CTA Button
                AppButton(
                  label: 'Plan Your Trip',
                  variant: AppButtonVariant.primary,
                  size: AppButtonSize.large,
                  isExpanded: true,
                  trailingIcon: Icons.arrow_forward,
                  customColor: AppColors.secondary,
                  onPressed: () => context.go(Routes.tripCreation),
                )
                    .animate(delay: const Duration(milliseconds: 800))
                    .fadeIn()
                    .slideY(begin: 0.3),

                const SizedBox(height: AppSpacing.lg),

                // Disclaimer
                Text(
                  'Free to use • No account required',
                  style: TextStyle(
                    fontSize: 12,
                    color: AppColors.white.withOpacity(0.6),
                  ),
                )
                    .animate(delay: const Duration(milliseconds: 900))
                    .fadeIn(),

                const SizedBox(height: AppSpacing.md),
              ],
            ),
          ),
        ),
      ),
    );
  }
}

class _FeatureItem extends StatelessWidget {
  final IconData icon;
  final String text;
  final Duration delay;

  const _FeatureItem({
    required this.icon,
    required this.text,
    required this.delay,
  });

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        Container(
          padding: const EdgeInsets.all(AppSpacing.sm),
          decoration: BoxDecoration(
            color: AppColors.white.withOpacity(0.15),
            borderRadius: BorderRadius.circular(AppSpacing.radiusSM),
          ),
          child: Icon(
            icon,
            color: AppColors.secondary,
            size: 20,
          ),
        ),
        const SizedBox(width: AppSpacing.md),
        Expanded(
          child: Text(
            text,
            style: TextStyle(
              fontSize: 14,
              color: AppColors.white.withOpacity(0.9),
            ),
          ),
        ),
      ],
    ).animate(delay: delay).fadeIn().slideX(begin: -0.2);
  }
}
