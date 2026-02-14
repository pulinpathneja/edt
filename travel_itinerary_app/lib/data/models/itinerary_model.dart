import 'package:freezed_annotation/freezed_annotation.dart';

import 'poi_model.dart';

part 'itinerary_model.freezed.dart';
part 'itinerary_model.g.dart';

/// Model for a time slot in a day's itinerary
@freezed
class TimeSlotModel with _$TimeSlotModel {
  const factory TimeSlotModel({
    @JsonKey(name: 'start_time') required String startTime,
    @JsonKey(name: 'end_time') required String endTime,
    required POIModel activity,
    TransportModel? transport,
    List<String>? notes,
  }) = _TimeSlotModel;

  factory TimeSlotModel.fromJson(Map<String, dynamic> json) =>
      _$TimeSlotModelFromJson(json);
}

/// Model for a single day in the itinerary
@freezed
class DayItineraryModel with _$DayItineraryModel {
  const factory DayItineraryModel({
    @JsonKey(name: 'day_number') required int dayNumber,
    required String date,
    String? title,
    String? summary,
    @JsonKey(name: 'time_slots') required List<TimeSlotModel> timeSlots,
    MealPOIModel? breakfast,
    MealPOIModel? lunch,
    MealPOIModel? dinner,
    @JsonKey(name: 'weather_note') String? weatherNote,
    List<String>? tips,
  }) = _DayItineraryModel;

  factory DayItineraryModel.fromJson(Map<String, dynamic> json) =>
      _$DayItineraryModelFromJson(json);
}

/// Model for the complete itinerary
@freezed
class ItineraryModel with _$ItineraryModel {
  const factory ItineraryModel({
    required String id,
    @JsonKey(name: 'destination_city') required String destinationCity,
    String? country,
    @JsonKey(name: 'start_date') required String startDate,
    @JsonKey(name: 'end_date') required String endDate,
    @JsonKey(name: 'total_days') required int totalDays,
    @JsonKey(name: 'group_type') required String groupType,
    @JsonKey(name: 'group_size') required int groupSize,
    required List<String> vibes,
    @JsonKey(name: 'budget_level') required int budgetLevel,
    required String pacing,
    String? title,
    String? overview,
    @JsonKey(name: 'hero_image_url') String? heroImageUrl,
    required List<DayItineraryModel> days,
    @JsonKey(name: 'general_tips') List<String>? generalTips,
    @JsonKey(name: 'packing_suggestions') List<String>? packingSuggestions,
    @JsonKey(name: 'estimated_budget') Map<String, dynamic>? estimatedBudget,
    @JsonKey(name: 'created_at') String? createdAt,
    @JsonKey(name: 'updated_at') String? updatedAt,
  }) = _ItineraryModel;

  factory ItineraryModel.fromJson(Map<String, dynamic> json) =>
      _$ItineraryModelFromJson(json);
}
