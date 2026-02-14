import 'package:freezed_annotation/freezed_annotation.dart';

part 'poi_model.freezed.dart';
part 'poi_model.g.dart';

/// Model for a Point of Interest (POI)
@freezed
class POIModel with _$POIModel {
  const factory POIModel({
    required String id,
    required String name,
    String? description,
    required String category,
    @JsonKey(name: 'start_time') String? startTime,
    @JsonKey(name: 'end_time') String? endTime,
    @JsonKey(name: 'duration_minutes') int? durationMinutes,
    String? address,
    double? latitude,
    double? longitude,
    @JsonKey(name: 'image_url') String? imageUrl,
    @JsonKey(name: 'rating') double? rating,
    @JsonKey(name: 'price_level') int? priceLevel,
    List<String>? tags,
    @JsonKey(name: 'booking_url') String? bookingUrl,
    @JsonKey(name: 'phone_number') String? phoneNumber,
    String? website,
    @JsonKey(name: 'opening_hours') Map<String, String>? openingHours,
    Map<String, dynamic>? tips,
  }) = _POIModel;

  factory POIModel.fromJson(Map<String, dynamic> json) =>
      _$POIModelFromJson(json);
}

/// Model for a meal/dining POI
@freezed
class MealPOIModel with _$MealPOIModel {
  const factory MealPOIModel({
    required String id,
    required String name,
    @JsonKey(name: 'meal_type') required String mealType, // breakfast, lunch, dinner
    String? cuisine,
    String? description,
    String? address,
    double? latitude,
    double? longitude,
    @JsonKey(name: 'image_url') String? imageUrl,
    double? rating,
    @JsonKey(name: 'price_level') int? priceLevel,
    @JsonKey(name: 'reservation_required') bool? reservationRequired,
    @JsonKey(name: 'booking_url') String? bookingUrl,
    @JsonKey(name: 'dietary_options') List<String>? dietaryOptions,
  }) = _MealPOIModel;

  factory MealPOIModel.fromJson(Map<String, dynamic> json) =>
      _$MealPOIModelFromJson(json);
}

/// Model for transportation between POIs
@freezed
class TransportModel with _$TransportModel {
  const factory TransportModel({
    required String mode, // walk, taxi, public_transit, etc.
    @JsonKey(name: 'duration_minutes') required int durationMinutes,
    String? description,
    double? distance,
    @JsonKey(name: 'estimated_cost') String? estimatedCost,
  }) = _TransportModel;

  factory TransportModel.fromJson(Map<String, dynamic> json) =>
      _$TransportModelFromJson(json);
}
