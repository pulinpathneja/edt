import 'package:freezed_annotation/freezed_annotation.dart';

part 'persona_config_model.freezed.dart';
part 'persona_config_model.g.dart';

/// Model for group type option
@freezed
class GroupTypeOptionModel with _$GroupTypeOptionModel {
  const factory GroupTypeOptionModel({
    required String id,
    required String label,
    required String icon,
    String? description,
  }) = _GroupTypeOptionModel;

  factory GroupTypeOptionModel.fromJson(Map<String, dynamic> json) =>
      _$GroupTypeOptionModelFromJson(json);
}

/// Model for vibe option
@freezed
class VibeOptionModel with _$VibeOptionModel {
  const factory VibeOptionModel({
    required String id,
    required String label,
    required String icon,
    String? description,
  }) = _VibeOptionModel;

  factory VibeOptionModel.fromJson(Map<String, dynamic> json) =>
      _$VibeOptionModelFromJson(json);
}

/// Model for pacing option
@freezed
class PacingOptionModel with _$PacingOptionModel {
  const factory PacingOptionModel({
    required String id,
    required String label,
    String? description,
  }) = _PacingOptionModel;

  factory PacingOptionModel.fromJson(Map<String, dynamic> json) =>
      _$PacingOptionModelFromJson(json);
}

/// Model for complete persona configuration
@freezed
class PersonaConfigModel with _$PersonaConfigModel {
  const factory PersonaConfigModel({
    @JsonKey(name: 'group_types') required List<GroupTypeOptionModel> groupTypes,
    required List<VibeOptionModel> vibes,
    @JsonKey(name: 'pacing_options') required List<PacingOptionModel> pacingOptions,
    @JsonKey(name: 'budget_min', defaultValue: 1) required int budgetMin,
    @JsonKey(name: 'budget_max', defaultValue: 5) required int budgetMax,
    @JsonKey(name: 'max_group_size', defaultValue: 20) required int maxGroupSize,
    @JsonKey(name: 'max_trip_days', defaultValue: 30) required int maxTripDays,
  }) = _PersonaConfigModel;

  factory PersonaConfigModel.fromJson(Map<String, dynamic> json) =>
      _$PersonaConfigModelFromJson(json);

  /// Create a default fallback configuration
  factory PersonaConfigModel.fallback() => const PersonaConfigModel(
        groupTypes: [
          GroupTypeOptionModel(id: 'solo', label: 'Solo', icon: '🧳'),
          GroupTypeOptionModel(id: 'couple', label: 'Couple', icon: '💑'),
          GroupTypeOptionModel(id: 'family', label: 'Family', icon: '👨‍👩‍👧‍👦'),
          GroupTypeOptionModel(id: 'friends', label: 'Friends', icon: '👯'),
        ],
        vibes: [
          VibeOptionModel(id: 'cultural', label: 'Cultural', icon: '🏛️'),
          VibeOptionModel(id: 'foodie', label: 'Foodie', icon: '🍕'),
          VibeOptionModel(id: 'adventure', label: 'Adventure', icon: '🏔️'),
          VibeOptionModel(id: 'relaxation', label: 'Relaxation', icon: '🏖️'),
          VibeOptionModel(id: 'romantic', label: 'Romantic', icon: '💕'),
          VibeOptionModel(id: 'nature', label: 'Nature', icon: '🌲'),
          VibeOptionModel(id: 'nightlife', label: 'Nightlife', icon: '🌃'),
          VibeOptionModel(id: 'shopping', label: 'Shopping', icon: '🛍️'),
        ],
        pacingOptions: [
          PacingOptionModel(id: 'slow', label: 'Slow', description: 'Relaxed pace'),
          PacingOptionModel(id: 'moderate', label: 'Moderate', description: 'Balanced'),
          PacingOptionModel(id: 'fast', label: 'Fast', description: 'Action-packed'),
        ],
        budgetMin: 1,
        budgetMax: 5,
        maxGroupSize: 20,
        maxTripDays: 30,
      );
}
