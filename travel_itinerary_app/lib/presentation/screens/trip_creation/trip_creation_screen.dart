import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../config/routes/app_router.dart';
import '../../../domain/entities/persona_config.dart';
import '../../controllers/trip_creation_controller.dart';
import '../../widgets/templates/wizard_template.dart';
import 'steps/constraints_step.dart';
import 'steps/destination_step.dart';
import 'steps/group_type_step.dart';
import 'steps/preferences_step.dart';
import 'steps/vibes_step.dart';

/// Multi-step trip creation wizard
class TripCreationScreen extends ConsumerWidget {
  const TripCreationScreen({super.key});

  static const stepLabels = [
    'Destination',
    'Group',
    'Vibes',
    'Preferences',
    'Constraints',
  ];

  static const stepTitles = [
    'Where are you going?',
    'Who\'s traveling?',
    'What\'s your vibe?',
    'Set your pace',
    'Any special needs?',
  ];

  static const stepSubtitles = [
    'Enter your destination and travel dates',
    'Tell us about your travel group',
    'Select the experiences you\'re looking for',
    'Choose your travel style and budget',
    'Help us personalize your itinerary',
  ];

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final state = ref.watch(tripCreationControllerProvider);
    final controller = ref.read(tripCreationControllerProvider.notifier);
    final configAsync = ref.watch(personaConfigProvider);

    return configAsync.when(
      data: (config) => _buildWizard(context, ref, state, controller, config),
      loading: () => const Scaffold(
        body: Center(child: CircularProgressIndicator()),
      ),
      error: (_, __) => _buildWizard(
        context,
        ref,
        state,
        controller,
        PersonaConfig.fallback(),
      ),
    );
  }

  Widget _buildWizard(
    BuildContext context,
    WidgetRef ref,
    TripCreationState state,
    TripCreationController controller,
    PersonaConfig config,
  ) {
    final currentStep = state.currentStep;
    final isStepValid = state.isStepValid(currentStep);
    final isLastStep = currentStep == TripCreationController.totalSteps - 1;

    return WizardTemplate(
      title: stepTitles[currentStep],
      subtitle: stepSubtitles[currentStep],
      totalSteps: TripCreationController.totalSteps,
      currentStep: currentStep,
      stepLabels: stepLabels,
      isNextEnabled: isStepValid,
      onBack: currentStep > 0 ? controller.previousStep : null,
      onNext: () {
        if (isLastStep && state.isValid) {
          // Navigate to generation with trip request
          context.go(Routes.generation);
        } else {
          controller.nextStep();
        }
      },
      child: _buildStepContent(currentStep, state, controller, config),
    );
  }

  Widget _buildStepContent(
    int step,
    TripCreationState state,
    TripCreationController controller,
    PersonaConfig config,
  ) {
    return switch (step) {
      0 => DestinationStep(
          destination: state.destinationCity,
          startDate: state.startDate,
          endDate: state.endDate,
          onDestinationChanged: controller.setDestination,
          onDateRangeChanged: controller.setDateRange,
          maxDays: config.maxTripDays,
        ),
      1 => GroupTypeStep(
          options: config.groupTypes,
          selectedType: state.groupType,
          groupSize: state.groupSize,
          hasKids: state.hasKids,
          hasSeniors: state.hasSeniors,
          onTypeChanged: controller.setGroupType,
          onGroupSizeChanged: controller.setGroupSize,
          onHasKidsChanged: controller.setHasKids,
          onHasSeniorsChanged: controller.setHasSeniors,
          maxGroupSize: config.maxGroupSize,
        ),
      2 => VibesStep(
          options: config.vibes,
          selectedVibes: state.vibes,
          onVibesChanged: controller.setVibes,
        ),
      3 => PreferencesStep(
          pacingOptions: config.pacingOptions,
          selectedPacing: state.pacing,
          budgetLevel: state.budgetLevel,
          budgetMin: config.budgetMin,
          budgetMax: config.budgetMax,
          onPacingChanged: controller.setPacing,
          onBudgetChanged: controller.setBudgetLevel,
        ),
      4 => ConstraintsStep(
          avoidHeat: state.avoidHeat,
          mobilityConstraints: state.mobilityConstraints,
          avoidCrowds: state.avoidCrowds,
          preferOutdoor: state.preferOutdoor,
          preferIndoor: state.preferIndoor,
          onAvoidHeatChanged: controller.setAvoidHeat,
          onMobilityConstraintsChanged: controller.setMobilityConstraints,
          onAvoidCrowdsChanged: controller.setAvoidCrowds,
          onPreferOutdoorChanged: controller.setPreferOutdoor,
          onPreferIndoorChanged: controller.setPreferIndoor,
        ),
      _ => const SizedBox.shrink(),
    };
  }
}
