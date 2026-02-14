import 'package:flutter/material.dart';
import 'package:riverpod_annotation/riverpod_annotation.dart';

import '../../config/di/providers.dart';
import '../../domain/entities/persona_config.dart';
import '../../domain/entities/trip_request.dart';

part 'trip_creation_controller.g.dart';

/// State for trip creation wizard
class TripCreationState {
  final int currentStep;
  final String destinationCity;
  final DateTime? startDate;
  final DateTime? endDate;
  final String groupType;
  final int groupSize;
  final bool hasKids;
  final bool hasSeniors;
  final Set<String> vibes;
  final int budgetLevel;
  final String pacing;
  final bool avoidHeat;
  final bool mobilityConstraints;
  final bool avoidCrowds;
  final bool preferOutdoor;
  final bool preferIndoor;

  const TripCreationState({
    this.currentStep = 0,
    this.destinationCity = '',
    this.startDate,
    this.endDate,
    this.groupType = 'solo',
    this.groupSize = 1,
    this.hasKids = false,
    this.hasSeniors = false,
    this.vibes = const {},
    this.budgetLevel = 3,
    this.pacing = 'moderate',
    this.avoidHeat = false,
    this.mobilityConstraints = false,
    this.avoidCrowds = false,
    this.preferOutdoor = false,
    this.preferIndoor = false,
  });

  TripCreationState copyWith({
    int? currentStep,
    String? destinationCity,
    DateTime? startDate,
    DateTime? endDate,
    String? groupType,
    int? groupSize,
    bool? hasKids,
    bool? hasSeniors,
    Set<String>? vibes,
    int? budgetLevel,
    String? pacing,
    bool? avoidHeat,
    bool? mobilityConstraints,
    bool? avoidCrowds,
    bool? preferOutdoor,
    bool? preferIndoor,
  }) {
    return TripCreationState(
      currentStep: currentStep ?? this.currentStep,
      destinationCity: destinationCity ?? this.destinationCity,
      startDate: startDate ?? this.startDate,
      endDate: endDate ?? this.endDate,
      groupType: groupType ?? this.groupType,
      groupSize: groupSize ?? this.groupSize,
      hasKids: hasKids ?? this.hasKids,
      hasSeniors: hasSeniors ?? this.hasSeniors,
      vibes: vibes ?? this.vibes,
      budgetLevel: budgetLevel ?? this.budgetLevel,
      pacing: pacing ?? this.pacing,
      avoidHeat: avoidHeat ?? this.avoidHeat,
      mobilityConstraints: mobilityConstraints ?? this.mobilityConstraints,
      avoidCrowds: avoidCrowds ?? this.avoidCrowds,
      preferOutdoor: preferOutdoor ?? this.preferOutdoor,
      preferIndoor: preferIndoor ?? this.preferIndoor,
    );
  }

  /// Convert to TripRequest for API
  TripRequest toTripRequest() {
    return TripRequest(
      destinationCity: destinationCity,
      startDate: startDate?.toIso8601String().split('T').first ?? '',
      endDate: endDate?.toIso8601String().split('T').first ?? '',
      groupType: groupType,
      groupSize: groupSize,
      hasKids: hasKids,
      hasSeniors: hasSeniors,
      vibes: vibes.toList(),
      budgetLevel: budgetLevel,
      pacing: pacing,
      avoidHeat: avoidHeat,
      mobilityConstraints: mobilityConstraints,
      avoidCrowds: avoidCrowds,
      preferOutdoor: preferOutdoor,
      preferIndoor: preferIndoor,
    );
  }

  /// Check if current step is valid
  bool isStepValid(int step) {
    return switch (step) {
      0 => destinationCity.isNotEmpty && startDate != null && endDate != null,
      1 => groupType.isNotEmpty && groupSize > 0,
      2 => vibes.isNotEmpty,
      3 => true, // Pacing and budget always have defaults
      4 => true, // Constraints are optional
      _ => false,
    };
  }

  /// Check if ready to submit
  bool get isValid =>
      destinationCity.isNotEmpty &&
      startDate != null &&
      endDate != null &&
      groupType.isNotEmpty &&
      vibes.isNotEmpty;

  /// Get trip duration in days
  int get tripDuration {
    if (startDate == null || endDate == null) return 0;
    return endDate!.difference(startDate!).inDays + 1;
  }
}

/// Controller for trip creation wizard
@riverpod
class TripCreationController extends _$TripCreationController {
  static const int totalSteps = 5;

  @override
  TripCreationState build() {
    return const TripCreationState();
  }

  void setDestination(String city) {
    state = state.copyWith(destinationCity: city);
  }

  void setDateRange(DateTimeRange range) {
    state = state.copyWith(
      startDate: range.start,
      endDate: range.end,
    );
  }

  void setGroupType(String type) {
    // Auto-set group size based on type
    final defaultSize = switch (type) {
      'solo' => 1,
      'couple' => 2,
      'family' => 4,
      'friends' => 4,
      _ => state.groupSize,
    };

    state = state.copyWith(
      groupType: type,
      groupSize: defaultSize,
    );
  }

  void setGroupSize(int size) {
    state = state.copyWith(groupSize: size);
  }

  void setHasKids(bool value) {
    state = state.copyWith(hasKids: value);
  }

  void setHasSeniors(bool value) {
    state = state.copyWith(hasSeniors: value);
  }

  void toggleVibe(String vibeId) {
    final newVibes = Set<String>.from(state.vibes);
    if (newVibes.contains(vibeId)) {
      newVibes.remove(vibeId);
    } else if (newVibes.length < 5) {
      newVibes.add(vibeId);
    }
    state = state.copyWith(vibes: newVibes);
  }

  void setVibes(Set<String> vibes) {
    state = state.copyWith(vibes: vibes);
  }

  void setBudgetLevel(int level) {
    state = state.copyWith(budgetLevel: level);
  }

  void setPacing(String pacing) {
    state = state.copyWith(pacing: pacing);
  }

  void setAvoidHeat(bool value) {
    state = state.copyWith(avoidHeat: value);
  }

  void setMobilityConstraints(bool value) {
    state = state.copyWith(mobilityConstraints: value);
  }

  void setAvoidCrowds(bool value) {
    state = state.copyWith(avoidCrowds: value);
  }

  void setPreferOutdoor(bool value) {
    state = state.copyWith(preferOutdoor: value);
  }

  void setPreferIndoor(bool value) {
    state = state.copyWith(preferIndoor: value);
  }

  void nextStep() {
    if (state.currentStep < totalSteps - 1) {
      state = state.copyWith(currentStep: state.currentStep + 1);
    }
  }

  void previousStep() {
    if (state.currentStep > 0) {
      state = state.copyWith(currentStep: state.currentStep - 1);
    }
  }

  void goToStep(int step) {
    if (step >= 0 && step < totalSteps) {
      state = state.copyWith(currentStep: step);
    }
  }

  void reset() {
    state = const TripCreationState();
  }
}

/// Provider for persona config (async)
@riverpod
Future<PersonaConfig> personaConfig(PersonaConfigRef ref) async {
  final repository = ref.watch(personaRepositoryProvider);
  return repository.getPersonaConfig();
}
