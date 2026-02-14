import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';

import '../../../theme/colors/app_colors.dart';
import '../../../theme/spacing/app_spacing.dart';
import '../atoms/app_button.dart';
import '../molecules/step_indicator.dart';

/// Template for multi-step wizard screens
class WizardTemplate extends StatelessWidget {
  final String title;
  final String? subtitle;
  final int totalSteps;
  final int currentStep;
  final List<String>? stepLabels;
  final Widget child;
  final VoidCallback? onBack;
  final VoidCallback? onNext;
  final String? nextLabel;
  final bool isNextEnabled;
  final bool isLoading;
  final bool showBackButton;

  const WizardTemplate({
    super.key,
    required this.title,
    this.subtitle,
    required this.totalSteps,
    required this.currentStep,
    this.stepLabels,
    required this.child,
    this.onBack,
    this.onNext,
    this.nextLabel,
    this.isNextEnabled = true,
    this.isLoading = false,
    this.showBackButton = true,
  });

  @override
  Widget build(BuildContext context) {
    final isFirstStep = currentStep == 0;
    final isLastStep = currentStep == totalSteps - 1;

    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(
        backgroundColor: Colors.transparent,
        elevation: 0,
        leading: showBackButton && !isFirstStep
            ? IconButton(
                icon: const Icon(Icons.arrow_back),
                onPressed: onBack,
              )
            : null,
        automaticallyImplyLeading: false,
      ),
      body: SafeArea(
        child: Column(
          children: [
            // Step indicator
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: AppSpacing.md),
              child: StepIndicator(
                totalSteps: totalSteps,
                currentStep: currentStep,
                stepLabels: stepLabels,
                showLabels: stepLabels != null,
              ),
            ),
            const SizedBox(height: AppSpacing.lg),

            // Title section
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: AppSpacing.md),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    title,
                    style: const TextStyle(
                      fontSize: 28,
                      fontWeight: FontWeight.w700,
                      color: AppColors.textPrimary,
                    ),
                  ).animate().fadeIn().slideX(begin: -0.1),
                  if (subtitle != null) ...[
                    const SizedBox(height: AppSpacing.sm),
                    Text(
                      subtitle!,
                      style: TextStyle(
                        fontSize: 16,
                        color: AppColors.textSecondary,
                      ),
                    ).animate().fadeIn(delay: const Duration(milliseconds: 100)).slideX(begin: -0.1),
                  ],
                ],
              ),
            ),
            const SizedBox(height: AppSpacing.xl),

            // Content
            Expanded(
              child: SingleChildScrollView(
                padding: const EdgeInsets.symmetric(horizontal: AppSpacing.md),
                child: child,
              ),
            ),

            // Bottom navigation
            Container(
              padding: const EdgeInsets.all(AppSpacing.md),
              decoration: BoxDecoration(
                color: AppColors.surface,
                border: Border(
                  top: BorderSide(color: AppColors.border),
                ),
              ),
              child: Row(
                children: [
                  // Back button
                  if (showBackButton && !isFirstStep)
                    Expanded(
                      child: AppButton(
                        label: 'Back',
                        variant: AppButtonVariant.outline,
                        onPressed: onBack,
                      ),
                    ),
                  if (showBackButton && !isFirstStep)
                    const SizedBox(width: AppSpacing.md),

                  // Next/Finish button
                  Expanded(
                    flex: showBackButton && !isFirstStep ? 2 : 1,
                    child: AppButton(
                      label: nextLabel ?? (isLastStep ? 'Generate Itinerary' : 'Continue'),
                      variant: AppButtonVariant.primary,
                      isExpanded: true,
                      isLoading: isLoading,
                      onPressed: isNextEnabled ? onNext : null,
                      trailingIcon: isLastStep ? Icons.auto_awesome : Icons.arrow_forward,
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}
