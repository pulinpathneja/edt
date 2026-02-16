import 'package:equatable/equatable.dart';
import 'itinerary.dart';

class InterCityTravel extends Equatable {
  final String fromCity;
  final String toCity;
  final String mode;
  final int durationMinutes;
  final String? departureTime;
  final String? notes;

  const InterCityTravel({
    required this.fromCity,
    required this.toCity,
    required this.mode,
    required this.durationMinutes,
    this.departureTime,
    this.notes,
  });

  String get durationDisplay {
    final hours = durationMinutes ~/ 60;
    final mins = durationMinutes % 60;
    if (hours == 0) return '${mins}min';
    if (mins == 0) return '${hours}h';
    return '${hours}h ${mins}min';
  }

  @override
  List<Object?> get props => [fromCity, toCity, mode, durationMinutes, departureTime, notes];
}

class CityItinerarySummary extends Equatable {
  final String cityId;
  final String cityName;
  final int days;
  final List<DayItinerary> dayItineraries;
  final InterCityTravel? travelToNext;
  final List<String>? highlights;

  const CityItinerarySummary({
    required this.cityId,
    required this.cityName,
    required this.days,
    required this.dayItineraries,
    this.travelToNext,
    this.highlights,
  });

  @override
  List<Object?> get props => [cityId, cityName, days, dayItineraries, travelToNext, highlights];
}

class CountryItinerary extends Equatable {
  final String id;
  final String countryId;
  final String countryName;
  final String startDate;
  final String endDate;
  final int totalDays;
  final String groupType;
  final List<String> vibes;
  final int budgetLevel;
  final String pacing;
  final List<CityItinerarySummary> cityItineraries;
  final List<String>? generalTips;
  final String? createdAt;

  const CountryItinerary({
    required this.id,
    required this.countryId,
    required this.countryName,
    required this.startDate,
    required this.endDate,
    required this.totalDays,
    required this.groupType,
    required this.vibes,
    required this.budgetLevel,
    required this.pacing,
    required this.cityItineraries,
    this.generalTips,
    this.createdAt,
  });

  int get totalActivities => cityItineraries.fold(0, (sum, c) => c.dayItineraries.fold(sum, (s, d) => s + d.activityCount));

  @override
  List<Object?> get props => [id, countryId, countryName, startDate, endDate, totalDays, groupType, vibes, budgetLevel, pacing, cityItineraries, generalTips, createdAt];
}
