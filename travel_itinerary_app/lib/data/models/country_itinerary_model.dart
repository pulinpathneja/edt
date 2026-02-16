import '../../domain/entities/country_itinerary.dart';
import '../../domain/entities/itinerary.dart';

class InterCityTravelModel extends InterCityTravel {
  const InterCityTravelModel({
    required super.fromCity,
    required super.toCity,
    required super.mode,
    required super.durationMinutes,
    super.departureTime,
    super.notes,
  });

  factory InterCityTravelModel.fromJson(Map<String, dynamic> json) {
    return InterCityTravelModel(
      fromCity: json['from_city'] as String? ?? '',
      toCity: json['to_city'] as String? ?? '',
      mode: json['mode'] as String? ?? 'train',
      durationMinutes: json['duration_minutes'] as int? ?? 0,
      departureTime: json['departure_time'] as String?,
      notes: json['notes'] as String?,
    );
  }
}

class CityItinerarySummaryModel extends CityItinerarySummary {
  const CityItinerarySummaryModel({
    required super.cityId,
    required super.cityName,
    required super.days,
    required super.dayItineraries,
    super.travelToNext,
    super.highlights,
  });

  factory CityItinerarySummaryModel.fromJson(Map<String, dynamic> json) {
    // Parse day itineraries from JSON manually since DayItineraryModel uses Freezed
    final daysList = <DayItinerary>[];
    if (json['day_itineraries'] != null) {
      for (final d in json['day_itineraries'] as List<dynamic>) {
        final dm = d as Map<String, dynamic>;
        daysList.add(DayItinerary(
          dayNumber: dm['day_number'] as int? ?? 0,
          date: dm['date'] as String? ?? '',
          title: dm['title'] as String?,
          summary: dm['summary'] as String?,
          timeSlots: const [],
          tips: dm['tips'] != null ? List<String>.from(dm['tips']) : null,
        ));
      }
    }

    return CityItinerarySummaryModel(
      cityId: json['city_id'] as String? ?? '',
      cityName: json['city_name'] as String? ?? '',
      days: json['days'] as int? ?? 0,
      dayItineraries: daysList,
      travelToNext: json['travel_to_next'] != null
          ? InterCityTravelModel.fromJson(json['travel_to_next'] as Map<String, dynamic>)
          : null,
      highlights: json['highlights'] != null ? List<String>.from(json['highlights']) : null,
    );
  }
}

class CountryItineraryModel extends CountryItinerary {
  const CountryItineraryModel({
    required super.id,
    required super.countryId,
    required super.countryName,
    required super.startDate,
    required super.endDate,
    required super.totalDays,
    required super.groupType,
    required super.vibes,
    required super.budgetLevel,
    required super.pacing,
    required super.cityItineraries,
    super.generalTips,
    super.createdAt,
  });

  factory CountryItineraryModel.fromJson(Map<String, dynamic> json) {
    return CountryItineraryModel(
      id: json['id'] as String? ?? '',
      countryId: json['country_id'] as String? ?? '',
      countryName: json['country_name'] as String? ?? '',
      startDate: json['start_date'] as String? ?? '',
      endDate: json['end_date'] as String? ?? '',
      totalDays: json['total_days'] as int? ?? 0,
      groupType: json['group_type'] as String? ?? '',
      vibes: List<String>.from(json['vibes'] ?? []),
      budgetLevel: json['budget_level'] as int? ?? 3,
      pacing: json['pacing'] as String? ?? 'moderate',
      cityItineraries: (json['city_itineraries'] as List<dynamic>?)
              ?.map((c) => CityItinerarySummaryModel.fromJson(c as Map<String, dynamic>))
              .toList() ??
          [],
      generalTips: json['general_tips'] != null ? List<String>.from(json['general_tips']) : null,
      createdAt: json['created_at'] as String?,
    );
  }
}
