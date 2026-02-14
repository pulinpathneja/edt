import 'package:equatable/equatable.dart';

/// Group type option entity
class GroupTypeOption extends Equatable {
  final String id;
  final String label;
  final String icon;
  final String? description;

  const GroupTypeOption({
    required this.id,
    required this.label,
    required this.icon,
    this.description,
  });

  @override
  List<Object?> get props => [id, label, icon, description];
}

/// Vibe option entity
class VibeOption extends Equatable {
  final String id;
  final String label;
  final String icon;
  final String? description;

  const VibeOption({
    required this.id,
    required this.label,
    required this.icon,
    this.description,
  });

  @override
  List<Object?> get props => [id, label, icon, description];
}

/// Pacing option entity
class PacingOption extends Equatable {
  final String id;
  final String label;
  final String? description;

  const PacingOption({
    required this.id,
    required this.label,
    this.description,
  });

  @override
  List<Object?> get props => [id, label, description];
}

/// Complete persona configuration entity
class PersonaConfig extends Equatable {
  final List<GroupTypeOption> groupTypes;
  final List<VibeOption> vibes;
  final List<PacingOption> pacingOptions;
  final int budgetMin;
  final int budgetMax;
  final int maxGroupSize;
  final int maxTripDays;

  const PersonaConfig({
    required this.groupTypes,
    required this.vibes,
    required this.pacingOptions,
    required this.budgetMin,
    required this.budgetMax,
    required this.maxGroupSize,
    required this.maxTripDays,
  });

  /// Get default/fallback configuration
  factory PersonaConfig.fallback() => const PersonaConfig(
        groupTypes: [
          GroupTypeOption(id: 'solo', label: 'Solo', icon: '🧳'),
          GroupTypeOption(id: 'couple', label: 'Couple', icon: '💑'),
          GroupTypeOption(id: 'family', label: 'Family', icon: '👨‍👩‍👧‍👦'),
          GroupTypeOption(id: 'friends', label: 'Friends', icon: '👯'),
        ],
        vibes: [
          VibeOption(id: 'cultural', label: 'Cultural', icon: '🏛️'),
          VibeOption(id: 'foodie', label: 'Foodie', icon: '🍕'),
          VibeOption(id: 'adventure', label: 'Adventure', icon: '🏔️'),
          VibeOption(id: 'relaxation', label: 'Relaxation', icon: '🏖️'),
          VibeOption(id: 'romantic', label: 'Romantic', icon: '💕'),
          VibeOption(id: 'nature', label: 'Nature', icon: '🌲'),
          VibeOption(id: 'nightlife', label: 'Nightlife', icon: '🌃'),
          VibeOption(id: 'shopping', label: 'Shopping', icon: '🛍️'),
        ],
        pacingOptions: [
          PacingOption(id: 'slow', label: 'Slow', description: 'Relaxed pace'),
          PacingOption(id: 'moderate', label: 'Moderate', description: 'Balanced'),
          PacingOption(id: 'fast', label: 'Fast', description: 'Action-packed'),
        ],
        budgetMin: 1,
        budgetMax: 5,
        maxGroupSize: 20,
        maxTripDays: 30,
      );

  @override
  List<Object?> get props => [
        groupTypes,
        vibes,
        pacingOptions,
        budgetMin,
        budgetMax,
        maxGroupSize,
        maxTripDays,
      ];
}
