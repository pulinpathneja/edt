class CityItinerarySummary {
  final String cityId;
  final String cityName;
  final int days;
  final String startDate;
  final String endDate;
  final List<String> highlights;
  final String? itineraryId;

  CityItinerarySummary({
    required this.cityId,
    required this.cityName,
    required this.days,
    required this.startDate,
    required this.endDate,
    this.highlights = const [],
    this.itineraryId,
  });

  factory CityItinerarySummary.fromJson(Map<String, dynamic> json) {
    return CityItinerarySummary(
      cityId: json['city_id'] ?? '',
      cityName: json['city_name'] ?? '',
      days: json['days'] ?? 1,
      startDate: json['start_date'] ?? '',
      endDate: json['end_date'] ?? '',
      highlights: List<String>.from(json['highlights'] ?? []),
      itineraryId: json['itinerary_id'],
    );
  }
}

class InterCityTravel {
  final String fromCity;
  final String toCity;
  final int? travelTimeMinutes;
  final String date;
  final String mode;

  InterCityTravel({
    required this.fromCity,
    required this.toCity,
    this.travelTimeMinutes,
    required this.date,
    this.mode = 'train',
  });

  factory InterCityTravel.fromJson(Map<String, dynamic> json) {
    return InterCityTravel(
      fromCity: json['from_city'] ?? '',
      toCity: json['to_city'] ?? '',
      travelTimeMinutes: json['travel_time_minutes'],
      date: json['date'] ?? '',
      mode: json['mode'] ?? 'train',
    );
  }

  String get travelTimeText {
    if (travelTimeMinutes == null) return 'Unknown';
    final hours = travelTimeMinutes! ~/ 60;
    final mins = travelTimeMinutes! % 60;
    if (hours == 0) return '${mins}min';
    return '${hours}h${mins > 0 ? ' ${mins}m' : ''}';
  }
}

class CountryItinerary {
  final String id;
  final String country;
  final String countryName;
  final int totalDays;
  final String startDate;
  final String endDate;
  final List<CityItinerarySummary> cityItineraries;
  final List<InterCityTravel> interCityTravel;
  final List<String> travelTips;

  CountryItinerary({
    required this.id,
    required this.country,
    required this.countryName,
    required this.totalDays,
    required this.startDate,
    required this.endDate,
    this.cityItineraries = const [],
    this.interCityTravel = const [],
    this.travelTips = const [],
  });

  factory CountryItinerary.fromJson(Map<String, dynamic> json) {
    return CountryItinerary(
      id: json['id'] ?? '',
      country: json['country'] ?? '',
      countryName: json['country_name'] ?? '',
      totalDays: json['total_days'] ?? 0,
      startDate: json['start_date'] ?? '',
      endDate: json['end_date'] ?? '',
      cityItineraries: (json['city_itineraries'] as List<dynamic>?)
              ?.map((c) => CityItinerarySummary.fromJson(c))
              .toList() ??
          [],
      interCityTravel: (json['inter_city_travel'] as List<dynamic>?)
              ?.map((t) => InterCityTravel.fromJson(t))
              .toList() ??
          [],
      travelTips: List<String>.from(json['travel_tips'] ?? []),
    );
  }
}
