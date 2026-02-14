import 'package:freezed_annotation/freezed_annotation.dart';

part 'trip_request_model.freezed.dart';
part 'trip_request_model.g.dart';

/// Model for trip generation request
@freezed
class TripRequestModel with _$TripRequestModel {
  const factory TripRequestModel({
    @JsonKey(name: 'destination_city') required String destinationCity,
    @JsonKey(name: 'start_date') required String startDate,
    @JsonKey(name: 'end_date') required String endDate,
    @JsonKey(name: 'group_type') required String groupType,
    @JsonKey(name: 'group_size') required int groupSize,
    @JsonKey(name: 'has_kids', defaultValue: false) required bool hasKids,
    @JsonKey(name: 'has_seniors', defaultValue: false) required bool hasSeniors,
    required List<String> vibes,
    @JsonKey(name: 'budget_level') required int budgetLevel,
    required String pacing,
    @JsonKey(name: 'avoid_heat', defaultValue: false) required bool avoidHeat,
    @JsonKey(name: 'mobility_constraints', defaultValue: false) required bool mobilityConstraints,
    @JsonKey(name: 'dietary_restrictions') List<String>? dietaryRestrictions,
    @JsonKey(name: 'special_interests') List<String>? specialInterests,
    @JsonKey(name: 'avoid_crowds', defaultValue: false) required bool avoidCrowds,
    @JsonKey(name: 'prefer_outdoor', defaultValue: false) required bool preferOutdoor,
    @JsonKey(name: 'prefer_indoor', defaultValue: false) required bool preferIndoor,
  }) = _TripRequestModel;

  factory TripRequestModel.fromJson(Map<String, dynamic> json) =>
      _$TripRequestModelFromJson(json);

  /// Create an empty/default trip request
  factory TripRequestModel.empty() => const TripRequestModel(
        destinationCity: '',
        startDate: '',
        endDate: '',
        groupType: 'solo',
        groupSize: 1,
        hasKids: false,
        hasSeniors: false,
        vibes: [],
        budgetLevel: 3,
        pacing: 'moderate',
        avoidHeat: false,
        mobilityConstraints: false,
        avoidCrowds: false,
        preferOutdoor: false,
        preferIndoor: false,
      );
}
