class CityAllocation {
  final String cityId;
  final String cityName;
  final int days;
  final String? arrivalFrom;
  final int? travelTimeMinutes;
  final List<String> highlights;

  CityAllocation({
    required this.cityId,
    required this.cityName,
    required this.days,
    this.arrivalFrom,
    this.travelTimeMinutes,
    this.highlights = const [],
  });

  factory CityAllocation.fromJson(Map<String, dynamic> json) {
    return CityAllocation(
      cityId: json['city_id'] ?? '',
      cityName: json['city_name'] ?? '',
      days: json['days'] ?? 1,
      arrivalFrom: json['arrival_from'],
      travelTimeMinutes: json['travel_time_minutes'],
      highlights: List<String>.from(json['highlights'] ?? []),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'city_id': cityId,
      'city_name': cityName,
      'days': days,
      'arrival_from': arrivalFrom,
      'travel_time_minutes': travelTimeMinutes,
      'highlights': highlights,
    };
  }
}

class AllocationOption {
  final int optionId;
  final String optionName;
  final String description;
  final List<CityAllocation> cities;
  final int totalDays;
  final int totalTravelTimeMinutes;
  final double matchScore;
  final List<String> pros;
  final List<String> cons;

  AllocationOption({
    required this.optionId,
    required this.optionName,
    required this.description,
    required this.cities,
    required this.totalDays,
    required this.totalTravelTimeMinutes,
    required this.matchScore,
    this.pros = const [],
    this.cons = const [],
  });

  factory AllocationOption.fromJson(Map<String, dynamic> json) {
    return AllocationOption(
      optionId: json['option_id'] ?? 1,
      optionName: json['option_name'] ?? '',
      description: json['description'] ?? '',
      cities: (json['cities'] as List<dynamic>?)
              ?.map((c) => CityAllocation.fromJson(c))
              .toList() ??
          [],
      totalDays: json['total_days'] ?? 0,
      totalTravelTimeMinutes: json['total_travel_time_minutes'] ?? 0,
      matchScore: (json['match_score'] ?? 0).toDouble(),
      pros: List<String>.from(json['pros'] ?? []),
      cons: List<String>.from(json['cons'] ?? []),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'option_id': optionId,
      'option_name': optionName,
      'description': description,
      'cities': cities.map((c) => c.toJson()).toList(),
      'total_days': totalDays,
      'total_travel_time_minutes': totalTravelTimeMinutes,
      'match_score': matchScore,
      'pros': pros,
      'cons': cons,
    };
  }

  String get travelTimeText {
    final hours = totalTravelTimeMinutes ~/ 60;
    final mins = totalTravelTimeMinutes % 60;
    if (hours == 0) return '${mins}min travel';
    return '${hours}h ${mins > 0 ? '${mins}m' : ''} travel';
  }

  int get matchPercent => (matchScore * 100).round();
}

class AllocationResponse {
  final String country;
  final String countryName;
  final int totalDays;
  final List<AllocationOption> options;
  final int recommendedOption;

  AllocationResponse({
    required this.country,
    required this.countryName,
    required this.totalDays,
    required this.options,
    required this.recommendedOption,
  });

  factory AllocationResponse.fromJson(Map<String, dynamic> json) {
    return AllocationResponse(
      country: json['country'] ?? '',
      countryName: json['country_name'] ?? '',
      totalDays: json['total_days'] ?? 0,
      options: (json['options'] as List<dynamic>?)
              ?.map((o) => AllocationOption.fromJson(o))
              .toList() ??
          [],
      recommendedOption: json['recommended_option'] ?? 0,
    );
  }
}
