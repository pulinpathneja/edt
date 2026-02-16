import '../../domain/entities/country.dart';

class CountryCityModel extends CountryCity {
  const CountryCityModel({
    required super.id,
    required super.name,
    required super.country,
    required super.minDays,
    required super.maxDays,
    required super.idealDays,
    required super.priority,
    required super.highlights,
    required super.vibes,
    required super.bestFor,
  });

  factory CountryCityModel.fromJson(Map<String, dynamic> json) {
    return CountryCityModel(
      id: json['id'] as String,
      name: json['name'] as String,
      country: json['country'] as String? ?? '',
      minDays: json['min_days'] as int? ?? 1,
      maxDays: json['max_days'] as int? ?? 5,
      idealDays: json['ideal_days'] as int? ?? 2,
      priority: json['priority'] as int? ?? 3,
      highlights: List<String>.from(json['highlights'] ?? []),
      vibes: List<String>.from(json['vibes'] ?? []),
      bestFor: List<String>.from(json['best_for'] ?? []),
    );
  }
}

class CountryModel extends Country {
  const CountryModel({
    required super.id,
    required super.name,
    required super.flag,
    required super.currency,
    required super.languages,
    required super.cities,
    required super.popularRoutes,
  });

  factory CountryModel.fromJson(Map<String, dynamic> json) {
    return CountryModel(
      id: json['id'] as String,
      name: json['name'] as String,
      flag: json['flag'] as String? ?? '',
      currency: json['currency'] as String? ?? '',
      languages: List<String>.from(json['languages'] ?? []),
      cities: (json['cities'] as List<dynamic>?)
              ?.map((c) => CountryCityModel.fromJson(c as Map<String, dynamic>))
              .toList() ??
          [],
      popularRoutes: (json['popular_routes'] as List<dynamic>?)
              ?.map((r) => List<String>.from(r as List<dynamic>))
              .toList() ??
          [],
    );
  }
}
